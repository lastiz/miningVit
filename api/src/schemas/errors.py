from .base import Base


class Error(Base):
    location: str
    message: str
    code: int | None = None


class ValidationErrorResponse(Base):
    detail: list[Error]
