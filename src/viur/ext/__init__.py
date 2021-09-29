import datetime
from . import version, utils, tasks


def parseInt(s, ret=0):
    """Parses a value as int
    """
    if not isinstance(s, str):
        return int(s)
    elif s:
        if s[0] in "+-":
            ts = s[1:]
        else:
            ts = s

        if ts and all([_ in "0123456789" for _ in ts]):
            return int(s)

    return ret


def parseBool(value: [str, bool]):
    """converts different truth values to boolean"""
    try:
        return str(value).lower() in {u"true", u"1", u"yes", u"ja"}
    except ValueError:
        return False


def datetimeFromIsoFormat(value: str):
    """convert ISO String to datetime object"""
    return datetime.datetime.strptime(value.split(".", 1)[0], "%Y-%m-%dT%H:%M:%S")


def cleanString(astring: str):
    """Convert a string to a ascii human-readable string

    :param astring: string
    :return: string
    """
    import unicodedata
    cleanname = str(unicodedata.normalize('NFKD', astring)
                    .encode('ASCII', 'ignore')
                    .decode("ASCII"))
    cleanname = ''.join(e for e in cleanname if e.isalnum())
    return cleanname.lower()
