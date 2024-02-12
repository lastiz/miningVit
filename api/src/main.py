from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import uvicorn
from sqladmin import Admin

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
from database.db import engine
from admin import views


# REDIS INIT
@asynccontextmanager
async def lifespan(app: FastAPI):
    await initiate_data.initiate_machines()
    await initiate_data.initiate_admin()
    await RedisService.init()
    yield
    await RedisService.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="MiningVit App",
        lifespan=lifespan,
        exception_handlers={RequestValidationError: validation_exception_handler},
        responses={
            422: {"description": "Validation Error", "model": ValidationErrorResponse}
        },
    )
    # routers
    app.include_router(auth_router, prefix="/auth")
    app.include_router(user_router, prefix="/api/user")
    app.include_router(finance_router, prefix="/api/finance")
    app.include_router(machine_router, prefix="/api/machine")

    # admin
    admin = Admin(
        app, engine, title="MiningVit Admin Panel", base_url="/" + settings.ADMIN_URL
    )
    admin.add_view(views.UserAdmin)
    admin.add_view(views.MasterReferralAdmin)
    admin.add_view(views.FinanceAdmin)
    admin.add_view(views.MachineAdmin)
    admin.add_view(views.PurchasedMachineAdmin)
    admin.add_view(views.DepositAdmin)
    admin.add_view(views.WithdrawalAdmin)
    admin.add_view(views.IncomeAdmin)
    admin.add_view(views.AdvertAdmin)

    @app.get("/")
    async def test():
        return settings.model_dump()

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run("main:app", reload=True)
