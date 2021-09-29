from viur.core import db
from viur.core import utils


def isRoot(user=None):
    """test if user is root, if missing user we use the currentUser

    :param user:
    :return: bool
    """
    if not user:
        user = utils.getCurrentUser()
    return user and "root" in user["access"]


def isGAEAdmin(user=None):
    """test if user is gaeAdmin, if missing user we use the currentUser

    :param user:
    :return: bool
    """
    if not user:
        user = utils.getCurrentUser()

    if user:
        return user.get("gaeadmin")

    return False
