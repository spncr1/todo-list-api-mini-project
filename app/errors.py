from fastapi import HTTPException, status


# Builds the standard 401 error used when a request has no usable login token.
def unauthorized_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    )


# Builds the standard 401 error used when login details do not match a user.
def invalid_credentials_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )


# Builds the standard 403 error used when a logged-in user does not own a resource.
def forbidden_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden",
    )


# Builds the standard 404 error used when a requested resource ID does not exist.
def not_found_error(resource_name: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource_name} not found",
    )


# Builds the standard 409 error used when a request conflicts with existing data.
def conflict_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
    )
