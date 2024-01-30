from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

# TODO: fix import problems ---------------------------------
import sys
from pathlib import Path

sys.path.append(str(Path(".").resolve() / "src"))
# TODO: fix import problems ---------------------------------

from routers.auth import router as auth_router
from routers.user import router as user_router
from dependencies.auth import get_current_user
from schemas.user import UserSchema
from schemas.errors import ValidationErrorResponse
from utils.error_handlers import validation_exception_handler
from services.redis_service import RedisService


# REDIS INIT
@asynccontextmanager
async def lifespan(app: FastAPI):
    await RedisService.init()
    yield
    await RedisService.close()


app = FastAPI(
    title="MiningVit App",
    lifespan=lifespan,
    exception_handlers={RequestValidationError: validation_exception_handler},
    responses={
        422: {"description": "Validation Error", "model": ValidationErrorResponse}
    },
)

app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/api/user")


@app.get("/")
async def tset(current_user: Annotated[UserSchema, Depends(get_current_user)]):
    return f"{id(app)}lololol"


@app.get("/lol")
async def lol(current_user: Annotated[UserSchema, Depends(get_current_user)]):
    return f"value = "
