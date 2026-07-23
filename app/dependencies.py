from fastapi import Header

from app import crud
from app.errors import unauthorized_error
from app.models import User


# Reads the Authorization header and returns the logged-in user for protected routes.
def get_current_user(authorization: str | None = Header(default=None)) -> User:
    if authorization is None:
        raise unauthorized_error()

    token = authorization.strip()

    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    if not token:
        raise unauthorized_error()

    user = crud.get_user_by_token(token)

    if user is None:
        raise unauthorized_error()

    return user
