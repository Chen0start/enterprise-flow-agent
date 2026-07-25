class AppError(Exception):
    """Base exception for application-level errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ResourceNotFoundError(AppError):
    """Raised when a requested resource does not exist."""


class ResourceConflictError(AppError):
    """Raised when a resource conflicts with existing data."""
