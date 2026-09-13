from typing import Any, Optional
from fastapi import HTTPException, status

class AppException(HTTPException):
    """
    Base custom application exception class.
    """
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "An internal application error occurred.",
        details: Optional[Any] = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.status_code = status_code
        self.message = message
        self.details = details

class EntityNotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message, details=details)

class AIServiceException(AppException):
    def __init__(self, message: str = "AI Service temporarily unavailable", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, message=message, details=details)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Could not validate credentials", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message, details=details)

class ForbiddenException(AppException):
    def __init__(self, message: str = "Insufficient permissions for this action", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message, details=details)

class RateLimitExceededException(AppException):
    def __init__(self, message: str = "Rate limit exceeded. Please slow down requests.", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, message=message, details=details)
