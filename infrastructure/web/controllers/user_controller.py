from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import uuid
import logging

from core.use_cases.user_use_cases import UserUseCases
from core.entities.user import User as UserEntity

from infrastructure.web.schemas import user_schemas, token_schemas
from infrastructure.web.dependencies.use_cases import get_user_use_case
from infrastructure.web.dependencies.auth import get_current_active_user
from infrastructure.auth.jwt_handler import jwt_handler

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# No need for get_user_use_cases helper here, use the dependency directly

@router.post("/register", response_model=user_schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: user_schemas.UserCreate,
    user_use_cases: UserUseCases = Depends(get_user_use_case) # Depend on the use case provider
    # No session dependency needed here
):
    """
    Register a new user. Session is managed via injected dependencies.
    """
    try:
        # Call use case method without session
        user = await user_use_cases.register_user(
            username=user_data.username,
            password=user_data.password,
            initial_credits=10,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Error during user registration for {user_data.username}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during registration")


@router.post("/token", response_model=token_schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_use_cases: UserUseCases = Depends(get_user_use_case) # Depend on use case provider
    # No session dependency needed here
):
    """
    Authenticate user and return JWT token. Session is managed via injected dependencies.
    """
    # Call use case method without session
    user = await user_use_cases.authenticate_user(
        username=form_data.username,
        password=form_data.password,
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = jwt_handler.create_access_token(
        data={"sub": user.username, "uid": str(user.id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=user_schemas.UserRead)
async def read_users_me(
    # This dependency handles auth and fetching user using its *own* session context if needed
    current_user: UserEntity = Depends(get_current_active_user)
):
    """
    Get current logged-in user's details.
    """
    return current_user


@router.get("/me/credits", response_model=dict)
async def get_my_credits(
    # Use the auth dependency to get the user ID/info securely
    current_user: UserEntity = Depends(get_current_active_user),
    # Use the use case dependency to perform the action
    user_use_cases: UserUseCases = Depends(get_user_use_case)
):
    """ Get the current user's credit balance using Use Case. Session managed implicitly. """
    try:
        # Use case handles fetching via its injected repo (which has the session)
        credits = await user_use_cases.check_user_credits(current_user.id)
        return {"username": current_user.username, "credits": credits}
    except ValueError as e: # User not found (shouldn't happen if authenticated)
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Error fetching credits for user {current_user.username}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not fetch credits.")
