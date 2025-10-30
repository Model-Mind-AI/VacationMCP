import os
import time
from collections import defaultdict, deque
from typing import Deque, DefaultDict
from fastapi import Header, HTTPException, status

API_KEY_ENV = "API_KEY"
API_KEY_HEADER = "X-API-Key"

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


def require_api_key(x_api_key: str | None = Header(default=None, alias=API_KEY_HEADER)) -> None:
    expected = os.getenv(API_KEY_ENV)
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    _check_rate_limit(x_api_key)
