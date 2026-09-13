import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("bizmatch.middleware")

class RequestLoggingAndTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique X-Request-ID UUID, measures latency (X-Process-Time),
    and structured-logs incoming HTTP requests.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        client_ip = request.client.host if request.client else "127.0.0.1"

        start_time = time.perf_counter()
        logger.info(f"[{request_id}] Incoming {request.method} {request.url.path} from IP: {client_ip}")

        response = await call_next(request)

        process_time = (time.perf_counter() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        response.headers["X-Request-ID"] = request_id

        logger.info(f"[{request_id}] {request.method} {request.url.path} finished in {process_time:.2f}ms [Status: {response.status_code}]")
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that injects security headers into all outgoing HTTP responses.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
