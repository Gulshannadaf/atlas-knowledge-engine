"""Rate limiting middleware using Redis."""

import time

from fastapi import HTTPException, status
from redis import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis sliding window.

    Limits requests per minute and per hour per client IP.
    """

    def __init__(self, app):
        super().__init__(app)
        self._redis: Redis | None = None

    @property
    def redis(self) -> Redis:
        if self._redis is None:
            self._redis = Redis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/live", "/health/ready", "/metrics"]:
            return await call_next(request)

        # Get client identifier (IP or user ID from token)
        client_id = self._get_client_id(request)

        # Check rate limits
        try:
            is_allowed, remaining, reset_time = self._check_rate_limit(client_id)
        except Exception:
            # If Redis fails, allow the request
            return await call_next(request)

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(settings.rate_limit_requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time - int(time.time())),
                },
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from request state (set by auth middleware)
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"

        # Handle X-Forwarded-For header
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        return f"ip:{client_ip}"

    def _check_rate_limit(self, client_id: str) -> tuple[bool, int, int]:
        """
        Check if client is within rate limits.

        Returns (is_allowed, remaining_requests, reset_timestamp)
        """
        now = int(time.time())
        minute_key = f"{settings.redis_prefix}ratelimit:{client_id}:minute"

        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()

        # Increment counter
        pipe.incr(minute_key)
        pipe.expire(minute_key, 60)

        results = pipe.execute()
        current_count = results[0]

        limit = settings.rate_limit_requests_per_minute
        remaining = max(0, limit - current_count)
        reset_time = now + 60

        is_allowed = current_count <= limit

        return is_allowed, remaining, reset_time
