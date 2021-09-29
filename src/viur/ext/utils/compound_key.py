import logging
from viur.core import db


def generateCompoundKey(kindName, keys, delimiter="$"):
    """Generate a db.Key from given keylist

    :param kindName: String
    :param keys: List ob keyStrings or keyObjects
    :param delimiter: String
    :return: db.KeyClass
    """
    ret = ""

    for key in keys:
        if ret:
            ret += delimiter

        if not isinstance(key, db.KeyClass):
            key = db.KeyClass.from_legacy_urlsafe(str(key))

        if key.id:
            ret += f"i{key.id}"
        else:
            ret += f"s{key.name}"

    return db.Key(kindName, ret)


def extractCompoundKey(key, kinds, delimiter="$"):
    """extract a list of keys form a CompoundKey

    :param key: CompoundKey
    :param kinds: List of Kindstrings
    :param delimiter: String
    :return: List of KeyObjects
    """
    assert isinstance(key, db.Key)

    ret = []

    try:
        for key in key.name().split(delimiter):
            kind = kinds.pop(0)

            if key[0] == "i":
                ret.append(db.Key(kind, int(key[1:])))
            else:
                ret.append(db.Key(kind, key[1:]))

    except:
        logging.error(f"Key '{str(key)}' seems to have an incorrect path")
        return None

    return ret
