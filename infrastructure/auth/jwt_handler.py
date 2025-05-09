import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from config.settings import settings

class JWTHandler:
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWTHandler.ACCESS_TOKEN_EXPIRE_MINUTES)
        data.update({"exp": expire})
        encoded_jwt = jwt.encode(data, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
            # Optionally add checks for 'sub' or other required claims
            # Check expiration time explicitly if needed, though jwt.decode handles it
            # expire_timestamp = payload.get("exp")
            # if expire_timestamp and datetime.now(timezone.utc) > datetime.fromtimestamp(expire_timestamp, tz=timezone.utc):
            #      # Token expired (although decode should raise JWTError for this)
            #      return None
            return payload
        except JWTError:
            # Token is invalid (expired, wrong signature, etc.)
            return None

jwt_handler = JWTHandler()
