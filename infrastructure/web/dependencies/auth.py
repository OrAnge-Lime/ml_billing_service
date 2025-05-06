from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# Remove AsyncSession import if no longer directly needed
# from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from infrastructure.auth.jwt_handler import jwt_handler # Import JWT handler for decoding
# Import repository dependency function and interface
from .repositories import get_user_repository
from core.repositories.user_repository import AbstractUserRepository # Import interface
from infrastructure.web.schemas.token_schemas import TokenData
from core.entities.user import User as UserEntity
# from .db import get_db_session # No longer needed directly here

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token") # Ensure path matches controller

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    # Depend on the repository provider dependency instead of session directly
    user_repo: AbstractUserRepository = Depends(get_user_repository) # Use the repo dependency
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
    user_id_str: str | None = payload.get("uid") # Assuming 'uid' stores user_id as string

    if username is None or user_id_str is None:
        raise credentials_exception

    # Use the injected repository instance (which already has the session)
    # Repository method now uses its internal session
    user = await user_repo.get_by_username(username=username)

    if user is None:
        # Log this case? Could indicate deleted user or token issue
        raise credentials_exception
    if not user.is_active:
         raise HTTPException(status_code=400, detail="Inactive user")

    # Compare user_id from token with fetched user's ID for extra safety
    if str(user.id) != user_id_str:
        # Log this? Indicates potential token mismatch or reuse
        raise credentials_exception # Token might be for a different user?

    return user # Return the core User entity

async def get_current_active_user(
    current_user: UserEntity = Depends(get_current_user)
) -> UserEntity:
    """
    Dependency wrapper to ensure the user is active (already checked by get_current_user).
    """
    # Check is implicitly done by get_current_user now
    return current_user
