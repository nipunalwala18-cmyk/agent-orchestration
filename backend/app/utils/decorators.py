import functools
from fastapi import Request
from app.core.exceptions import AppException
from app.models.user import User


def require_permission(permission_name: str):
    """Decorator to assert that the logged-in user possesses the required permission.

    Assumes that get_current_user has run and populated request.state.user.
    Make sure to declare `request: Request` in your route parameters.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Locate Request object in route parameters
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                raise AppException(
                    "Request object not found in endpoint signature. "
                    "Make sure to declare `request: Request` in your route parameters.",
                    status_code=500,
                )

            user: User = getattr(request.state, "user", None)
            if not user:
                raise AppException("Authentication required.", status_code=401)

            user_permissions = set()
            for role in user.roles:
                for perm in role.permissions:
                    user_permissions.add(perm.name)

            if permission_name not in user_permissions:
                raise AppException("Permission denied.", status_code=403)

            return await func(*args, **kwargs)

        return wrapper

    return decorator
