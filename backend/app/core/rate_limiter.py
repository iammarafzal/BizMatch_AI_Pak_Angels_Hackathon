import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger("bizmatch.rate_limiter")

def safe_get_remote_address(request: Request) -> str:
    """Safe IP extractor that handles missing client object in ASGI/proxied requests."""
    try:
        if request.client and request.client.host:
            return request.client.host
    except Exception:
        pass
    return "127.0.0.1"

limiter = Limiter(
    key_func=safe_get_remote_address,
    default_limits=["60 per minute"]
)

def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom 429 response handler formatted cleanly for client consumption.
    """
    client_ip = safe_get_remote_address(request)
    logger.warning(f"Rate limit exceeded for client IP {client_ip} on path {request.url.path}")
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
