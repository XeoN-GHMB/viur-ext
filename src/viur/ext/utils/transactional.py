import logging
from viur.core import db, skeleton
from viur.core.utils import normalizeKey
from typing import Dict


def setStatus(
        key: db.Key,
        values: Dict = None,
        check: Dict = None,
        create: [Dict, bool] = None,
        func: callable = None,
        skel: skeleton.BaseSkeleton = None
):
    """
    Universal function to set a status of an entity within a transaction.
    :param key: Entity key to change
    :param values: A dict of key-values to update on the entry
    :param check: An optional dict of key-values to check on the entry before
    :param create: When key does not exist, create it, optionally with values from provided dict.
    :param func: A function that is called inside the transaction
    :param skel: Use assigned skeleton instead of low-level DB-API
    If the function does not raise an Exception, all went well.
    It returns either the assigned skel, or the db.Entity on success.
    """
    assert isinstance(values, dict) or values is None, "'values' has to be a dict, you diggi!"

    def transaction():
        if skel:
            if skel.fromDB(key):
                exists = True
            else:
                if not create:
                    raise ValueError("Entity with key %r not found" % key)

                skel["key"] = key
                exists = False

            obj = skel
        else:
            try:
                obj = db.Get(key)
                exists = True

            except:  # fixme: except EntityNotFound only?
                if not create:
                    raise

                obj = None

            if obj is None:
                exists = False
                obj = db.Entity(key)

        if not exists and isinstance(create, dict):
            for bone, value in create.items():
                obj[bone] = value

        if check:
            assert isinstance(check, dict), "'check' has to be a dict, you diggi!"

            for bone, value in check.items():
                assert obj[bone] == value, "%r contains %r, expecting %r" % (bone, obj[bone], value)

        if values:
            for bone, value in values.items():
                if bone[0] == "+":
                    obj[bone[1:]] += value
                elif bone[0] == "-":
                    obj[bone[1:]] -= value
                else:
                    obj[bone] = value

        if func and callable(func):
            func(obj)

        if skel:
            assert skel.toDB(clearUpdateTag=True)
        else:
            db.Put(obj)

        return obj

    return db.RunInTransaction(transaction)


def writeInTransaction(key: db.Key, createMissingEntity=True, **values: dict):
    """Write given values in a transaction to the database.

    In case the key is missing a new Entity is created.
    """

    return setStatus(key,
                     values=values,
                     create=values if createMissingEntity else None)


def increaseCounter(key: db.Key, name: str, value=1, start=0):
    """increase a attribute in a Entry by the amount of value. If not exists create it with start value"""
    return setStatus(key,
                     values={f"+{name}": value},
                     create={name: start})
