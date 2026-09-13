import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger("bizmatch.rate_limiter")

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60 per minute"]
)

def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom 429 response handler formatted cleanly for client consumption.
    """
    logger.warning(f"Rate limit exceeded for client IP {get_remote_address(request)} on path {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        headers={"Retry-After": "60"},
        content={
            "success": False,
            "error": "Rate limit exceeded. Please try again in 60 seconds.",
            "code": 429,
            "details": f"Threshold breached: {exc.detail}"
        }
    )
