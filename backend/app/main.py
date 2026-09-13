import time
import logging
import traceback
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.exceptions import AppException
from app.core.middleware import RequestLoggingAndTimingMiddleware, SecurityHeadersMiddleware
from app.core.rate_limiter import limiter, custom_rate_limit_handler
from app.services.seeder import seed_database_if_empty

# Ensure all SQLAlchemy models are registered
import app.models.business
import app.models.manager
import app.models.match
import app.models.user

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("bizmatch.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database tables exist on application startup and auto-seed if empty."""
    from starlette.concurrency import run_in_threadpool
    await run_in_threadpool(Base.metadata.create_all, bind=engine)
    logger.info("Database tables initialized successfully.")
    try:
        await run_in_threadpool(seed_database_if_empty)
    except Exception as e:
        logger.warning(f"Auto-seed warning: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="BizMatch AI - High-velocity match and explainability engine connecting businesses with vetted fractional and full-time leaders.",
    lifespan=lifespan
)

# Attach SlowAPI Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# Custom Global Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"AppException [{exc.status_code}] on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "details": exc.details,
            "code": exc.status_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", [])])
        formatted_errors.append(f"{field}: {err.get('msg')}")
    
    logger.warning(f"Validation error on {request.url.path}: {formatted_errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": formatted_errors,
            "code": 422
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    error_trace = traceback.format_exc()
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}:\n{error_trace}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "code": 500
        }
    )

# Register Custom Middleware Pipeline
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingAndTimingMiddleware)

# CORS Middleware: allow configured origins, Vercel preview/prod domains, and standard headers
cors_origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https://.*\.vercel\.app$" if "*" not in cors_origins else None,
    allow_credentials=True if "*" not in cors_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
@limiter.limit("60/minute")
async def health_check(request: Request):
    return {"status": "healthy", "service": settings.PROJECT_NAME}

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

