from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

# TODO: fix import problems ---------------------------------
import sys
from pathlib import Path

sys.path.append(str(Path(".").resolve() / "src"))
# TODO: fix import problems ---------------------------------

from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.finance import router as finance_router
from routers.machine import router as machine_router
from schemas.errors import ValidationErrorResponse
from utils.error_handlers import validation_exception_handler
from services.redis_service import RedisService
from utils import initiate_data
from config import settings


# REDIS INIT
@asynccontextmanager
async def lifespan(app: FastAPI):
    await initiate_data.initiate_machines()
    await initiate_data.initiate_admin()
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
app.include_router(finance_router, prefix="/api/finance")
app.include_router(machine_router, prefix="/api/machine")


@app.get("/")
async def test():
    return settings.model_dump()
