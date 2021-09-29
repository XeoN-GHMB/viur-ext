import logging
from viur.core import db, errors, utils, conf, skeleton

conf["viur.ext.utils.skelForRequest.prefix"] = "@"


def setSkelForRequest(skelName, skel):
    """Set a skeleton for the current request.

    It is the opposite of getSkelForRequest() below.
    """
    if isinstance(skel, skeleton.SkeletonInstance):
        key = skel["key"].to_legacy_urlsafe().decode("ASCII")

        reqData = utils.currentRequestData.get()
        reqData[f'{skelName}.{key}'] = skel

    elif isinstance(skel, db.KeyClass):
        key = skel.to_legacy_urlsafe().decode("ASCII")

    else:
        assert isinstance(skel, str), "key must be a str"
        key = skel

    utils.currentRequest.get().kwargs[f'{conf["viur.ext.utils.skelForRequest.prefix"]}{skelName}'] = key


def getSkelForRequest(moduleName, key=None, attr=None, optional=True, skelName=None):
    """Retrieve a skeleton with a key and caches it in the current request.

    If no key is given, the function tries to retrieve the key for the requested object
    from the request parameters, by preceding an "@" sign to the skelName as parameter.
    So adding "@project=abc" will try to load a "project"-Skeleton with the key "abc".
    When the skeleton is requested multiple times, only the already loaded version is
    immediately returned.
    """
    if skelName is None:
        skelName = moduleName

    if key is None:
        paramKey = f'{conf["viur.ext.utils.skelForRequest.prefix"]}{moduleName}'

        req = utils.currentRequest.get()
        if not req:
            return None

        key = req.kwargs.get(paramKey)
        if key is None or not key:
            if not optional:
                logging.error("Required parameter %r not found", paramKey)
                raise errors.MethodNotAllowed(f"Parameter {paramKey} required")

            return None

    if isinstance(key, db.KeyClass):
        key = key.to_legacy_urlsafe().decode("ASCII")
    else:
        assert isinstance(key, str), "key must be a str"

    reqData = utils.currentRequestData.get()

    if f'{skelName}.{key}' in reqData.keys():
        skel = reqData[f'{skelName}.{key}']

        if skel and attr is not None:
            return skel[attr]

        return skel

    skel = skeleton.skeletonByKind(skelName)
    if skel:
        skel = skel()

        if skel.fromDB(key):
            skel = skel.clone()
        else:
            skel = None

    # Check module's canView function for security
    mod = getattr(conf["viur.mainApp"], moduleName, None)
    if mod:
        if not mod.canView(skel):
            raise errors.Unauthorized(f"Insufficient rights to access entity '{key}' of module '{moduleName}'")

    reqData[f'{skelName}.{key}'] = skel

    if skel and attr is not None:
        return skel[attr]

    return skel
