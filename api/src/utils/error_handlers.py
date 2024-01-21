from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from schemas.errors import ValidationErrorResponse, Error


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Format the pydantic ValidationErrors in a more human-readable way.
    """

    errors = [
        Error(location=err["loc"][-1], message=err["msg"], code=err.get("code", 422))
        for err in exc.errors()
    ]

    error_res = ValidationErrorResponse(detail=errors)
    return JSONResponse(
        content=jsonable_encoder({"detail": error_res.detail}),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
