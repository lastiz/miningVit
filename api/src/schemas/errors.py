from pydantic import BaseModel, ConfigDict


class Error(BaseModel):
    location: str
    message: str
    code: int | None = None


class ValidationErrorResponse(BaseModel):
    detail: list[Error]
