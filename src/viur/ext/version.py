"""provide a simple api to get version information"""
import os


def isDevServer():
    """Test function to detect development servers.

    Returns true if we are local else False
    :return: bool
    """
    if "GAE_ENV" in os.environ and os.environ["GAE_ENV"] == "standard":
        return False
    return True


def currentApp():
    """This function returns the application id

    :return: string
    """
    return os.environ["GOOGLE_CLOUD_PROJECT"]


def currentVersion():
    """The function returns the current Version

    if we are local this would be a timestamp
    :return: string
    """
    return os.environ["GAE_VERSION"]


def isDefault():
    """This function returns True if the current Version is a live Version
    google-cloud-appengine-admin>=1.1.3
    :return: bool
    """
    raise NotImplementedError("Requires Admin Api enabled + access rights")
