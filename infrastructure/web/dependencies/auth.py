from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from infrastructure.auth.jwt_handler import jwt_handler 
from .repositories import get_user_repository
from core.repositories.user_repository import AbstractUserRepository
from core.entities.user import User as UserEntity

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: AbstractUserRepository = Depends(get_user_repository)
) -> UserEntity:
    """
    Dependency to get the current authenticated user from the token.
    Uses injected repository (which contains the request-scoped session).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = jwt_handler.decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str | None = payload.get("sub")
    user_id_str: str | None = payload.get("uid")

    if username is None or user_id_str is None:
        raise credentials_exception

    user = await user_repo.get_by_username(username=username)

    if user is None:
        raise credentials_exception
    if not user.is_active:
         raise HTTPException(status_code=400, detail="Inactive user")

    if str(user.id) != user_id_str:
        raise credentials_exception 

    return user

async def get_current_active_user(
    current_user: UserEntity = Depends(get_current_user)
) -> UserEntity:
    """
    Dependency wrapper to ensure the user is active (already checked by get_current_user).
    """
    # Check is implicitly done by get_current_user now
    return current_user
