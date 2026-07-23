from fastapi import APIRouter, status

from app import crud
from app.errors import conflict_error, invalid_credentials_error
from app.schemas import TokenRead, UserCreate, UserLogin, UserRead


router = APIRouter(tags=["auth"])

# User Registration endpoint
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    user = crud.create_user(user_data)

    if user is None:
        raise conflict_error("Email already registered")

    return user

# User Login endpoint
@router.post("/login", response_model=TokenRead)
async def login(login_data: UserLogin):
    token = crud.login_user(login_data)

    if token is None:
        raise invalid_credentials_error()

    return TokenRead(token=token)
