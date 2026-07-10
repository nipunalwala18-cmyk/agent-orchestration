from typing import Any, Optional


class AppException(Exception):
    """Base application exception for custom domain exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class DatabaseException(AppException):
    """Exception raised for database operations or transactional failures."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message, status_code=500, details=details)


class AgentException(AppException):
    """Exception raised for failures in agent logic, execution, or validation."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message, status_code=status_code, details=details)


class ToolException(AppException):
    """Exception raised for errors during tool execution or parameter mapping."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message, status_code=status_code, details=details)


class WorkflowException(AppException):
    """Exception raised during stateful or graph-based agent flow execution."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message, status_code=status_code, details=details)
