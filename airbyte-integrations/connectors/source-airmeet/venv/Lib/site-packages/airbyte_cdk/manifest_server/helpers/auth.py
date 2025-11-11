import os
from typing import Optional

import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


def verify_jwt_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> None:
    """
    Verify JWT token if AB_JWT_SIGNATURE_SECRET is set, otherwise allow through.

    Args:
        credentials: Bearer token credentials from request header

    Raises:
        HTTPException: If token is invalid or missing when secret is configured
    """
    jwt_secret = os.getenv("AB_JWT_SIGNATURE_SECRET")

    # If no secret is configured, allow all requests through
    if not jwt_secret:
        return

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        jwt.decode(credentials.credentials, jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
