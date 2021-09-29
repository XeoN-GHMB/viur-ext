import functools, json, logging, types
from viur.core import utils, errors, securitykey
from viur.core.utils import currentRequest

__all__ = ["rolesRequired", "asJsonResponse", "skeyRequired", "debug"]

logger = logging.getLogger(__name__)


def rolesRequired(*requiredRoles):
    """Decorator, which performs the authentication and authorization check.

    To expose a method only to logged in users with the access
    "root" or ("admin" and "file-edit") or "maintainer"
    use this decorator like this:

    >>> from viur.core import exposed
    >>> from viur.ext.decorators import rolesRequired
    >>> @exposed
    >>> @rolesRequired("root", ["admin", "file-edit"], ["maintainer"])
    >>> def yourMethod(self):
    >>>		return "You're allowed!"
    """

    def outerWrapper(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            user = utils.getCurrentUser()
            if not user:
                raise errors.Unauthorized()

            for role in requiredRoles:
                if isinstance(role, str):
                    role = [role]
                assert isinstance(role, (tuple, list, set))

                missingRole = set(role).difference(user["access"])
                if not missingRole:
                    return f(*args, **kwargs)

            logger.error("%s requires role %s", f.__name__, " OR ".join(map(repr, requiredRoles)))
            raise errors.Forbidden()

        return wrapper

    assert requiredRoles, "No rules set"
    return outerWrapper


def skeyRequired(func=None, **decoratorKwArgs):
    """Decorator that checks the skey before the method is called.

    Optional callable to pass keyword-arguments for the securitykey.validate-call.

    Example:
        >>> from viur.core import exposed
        >>> @exposed
        >>> @skeyRequired
        >>> def yourMethod(self):
        >>>     return {"foo": "bar"}
    """

    def outerWrapper(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not securitykey.validate(kwargs.pop("skey", ""), **decoratorKwArgs):
                raise errors.PreconditionFailed("Missing or invalid skey")
            return f(*args, **kwargs)

        return wrapper

    if isinstance(func, (types.MethodType, types.FunctionType)):
        return outerWrapper(func)  # @skeyRequired
    else:
        return outerWrapper  # @skeyRequired() or @skeyRequired(**anyKwargs)


def asJsonResponse(func=None, **decoratorKwArgs):
    """Decorator that returns the method/function response json serialized.

    Optional callable to pass keyword-arguments for the json.dumps-call.

    Example:
        >>> from viur.core import exposed
        >>> @exposed
        >>> @asJsonResponse(default=str)
        >>> def yourMethod(self):
        >>>     return {"foo": "bar"}
    """

    def outerWrapper(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            currentRequest.get().response.headers["Content-Type"] = "application/json"
            return json.dumps(f(*args, **kwargs), **decoratorKwArgs)

        return wrapper

    if isinstance(func, (types.MethodType, types.FunctionType)):
        return outerWrapper(func)  # @asJsonResponse
    else:
        return outerWrapper  # @asJsonResponse() or @asJsonResponse(**anyKwargs)


def debug(func):
    """Decorator to print the function signature and return value
    """

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = map(repr, args)
        kwargs_repr = [f"{k}={v}" for k, v in kwargs.items()]
        signature = ", ".join(list(args_repr) + kwargs_repr)
        logger.info("CALLING %s(%s)", func.__name__, signature)
        value = func(*args, **kwargs)
        logger.info("%r RETURNED %r", func.__name__, value)
        return value

    return wrapper_debug
