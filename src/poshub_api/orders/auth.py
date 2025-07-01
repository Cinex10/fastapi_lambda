import os
from typing import Callable, List

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

security = HTTPBearer()


def validate_jwt_and_scope(required_scopes: List[str]) -> Callable:
    def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
        token = credentials.credentials
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        scopes = payload.get("scopes", "").split()
        for scope in required_scopes:
            if scope not in scopes:
                model, action = scope.split(":")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission to {} {}".format(
                        action, model
                    ),
                )
        return payload

    return dependency
