import os
import time
from collections import defaultdict, deque
from typing import Deque, DefaultDict
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

API_KEY_ENV = "API_KEY"

# OAuth2 Bearer token security scheme
security = HTTPBearer()

# naive in-memory rate limiter: 60 requests per 60 seconds per API key
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 60
_key_to_hits: DefaultDict[str, Deque[float]] = defaultdict(deque)


def _check_rate_limit(key: str) -> None:
    now = time.time()
    q = _key_to_hits[key]
    # drop old
    while q and now - q[0] > _WINDOW_SECONDS:
        q.popleft()
    if len(q) >= _MAX_REQUESTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    q.append(now)


def require_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> None:
    """
    OAuth2 Bearer token authentication.
    Expects Authorization header: 'Bearer <API_KEY>'
    The API key is passed as the Bearer token.
    """
    token = credentials.credentials
    expected = os.getenv(API_KEY_ENV)
    
    if not expected or token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _check_rate_limit(token)
