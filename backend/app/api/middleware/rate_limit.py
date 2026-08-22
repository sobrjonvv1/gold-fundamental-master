"""Small in-process rate limiter for the public API.

For multiple web instances, put an edge rate limit in front of the service too.
"""

from collections import defaultdict, deque
from time import monotonic

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.windows: dict[str, deque[float]] = defaultdict(deque)

    def _client_key(self, request) -> str:
        if settings.TRUST_PROXY_HEADERS:
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",", 1)[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request, call_next):
        if not request.url.path.startswith("/api/") or request.method == "OPTIONS":
            return await call_next(request)

        now = monotonic()
        requests = self.windows[self._client_key(request)]
        while requests and now - requests[0] >= 60:
            requests.popleft()
        if len(requests) >= self.requests_per_minute:
            retry_after = max(1, int(60 - (now - requests[0])))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again shortly."},
                headers={"Retry-After": str(retry_after)},
            )
        requests.append(now)
        return await call_next(request)
