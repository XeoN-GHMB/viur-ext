import logging, safeeval
from viur.core import errors, utils, skeleton, tasks
from viur.core.bones import baseBone, selectBone, stringBone


@tasks.CallableTask
class TaskClearKind(tasks.CallableTaskBase):
    key = "clearKind"
    name = "Clear all entities of a kind"
    descr = "This task can be called to clean your database from a specific kind."

    def canCall(self):
        user = utils.getCurrentUser()
        return user is not None and "root" in user["access"]

    def dataSkel(self):
        skel = skeleton.BaseSkeleton().clone()
        skel.module = selectBone(
            descr="Module",
            values=skeleton.listKnownSkeletons(),
            required=True,
            multiple=True
        )
        skel.eval = baseBone(
            descr="Eval",
            params={
                "tooltip": "Enter a SafeEval-Python expression here to filter entries by specific bone values."
            },
            validHtml=None
        )
        skel.confirm = stringBone(
            descr="Type YES as your confirmation!",
            required=True
        )
        return skel

    def execute(self, module, confirm, eval=None, *args, **kwargs):
        if confirm != "YES":
            raise errors.PreconditionFailed("Confirm must be 'YES'!")

        if eval and eval.strip():
            try:
                safeeval.SafeEval().compile(eval)
            except SyntaxError as e:
                logging.exception(e)
                raise errors.PreconditionFailed("The expression is not valid")

        usr = utils.getCurrentUser()
        if not usr:
            logging.warning("Don't know who to inform after rebuilding finished")
            notify = None
        else:
            notify = usr["name"]

        @tasks.callDeferred
        def processChunk(module, eval=None, notify=None, cursor=None, total=0):
            Skel = skeleton.skeletonByKind(module)
            if not Skel:
                logging.error("Invalid module %r", module)
                return

            query = Skel().all().setCursor(cursor)

            lol = safeeval.SafeEval()

            if eval and eval.strip():
                ast = lol.compile(eval)
            else:
                ast = None

            for obj in query.run(99):
                total += 1

                skel = Skel()
                if not skel.fromDB(obj.key):
                    logging.warning("Cannot remove %r, it doesn't exist", obj.key)
                    continue

                if ast and not lol.execute(ast, skel):
                    logging.info("The eval expression prohibits deletion of %r, its what you wanted :)", obj.key)
                    continue

                skel.delete()

            cursor = query.getCursor()
            if not cursor:  # We're done
                try:
                    if notify:
                        txt = ("Subject: Clearing %s done\n\n" +
                               "ViUR finished to clear all entries of %s.\n" +
                               "%d records updated in total on this kind.") % (module, module, total)
                        utils.sendEMail([notify], txt, None)
                except:  # OverQuota, whatever
                    pass

                logging.info("Finished clearing %d entries of %r", total, module)
                return

            logging.debug("Cleared %d entries of %r so far", total, module)
            processChunk(module, eval, notify, cursor, total)

        for mod in module:
            processChunk(mod, eval, notify=notify)
