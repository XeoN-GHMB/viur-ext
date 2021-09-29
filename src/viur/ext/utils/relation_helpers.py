from viur.core import utils, db, skeleton
from typing import Union


def addToRelation(skel, boneName: str, key: db.KeyClass, using: Union[skeleton.RelSkel, None] = None):
    """adds a key to a relationalbone"""
    if using:
        entry = (key, using)
    else:
        entry = key

    getattr(skel, boneName).setBoneValue(skel, boneName, entry, append=True)
    return skel


def removeFromRelation(skel, boneName: str, key: db.KeyClass):
    """removes a key from a relationalbone"""
    newValue = []
    bone = getattr(skel, boneName)

    for x in skel[boneName]:
        if x["dest"]["key"] != key:

            if bone.using:
                newValue.append((x["dest"]["key"], x["rel"]))
            else:
                newValue.append(x["dest"]["key"])

    getattr(skel, boneName).setBoneValue(skel, boneName, newValue, append=False)
    return skel
