from repositories.machine_repository import MachineRepository
from repositories.UserRepository import UserRepository
from repositories.finance_repository import FinanceRepository
from schemas.user import UserSchema
from utils.security import SecurityHasher
from config import settings
from database.db import async_session_maker


async def initiate_machines() -> None:
    async with async_session_maker() as session:
        repo = MachineRepository(session)

        machines = await repo.list()
        if machines:
            return

        for machine_data in settings.MACHINES_INFO:
            await repo.add(machine_data)

        await session.commit()


async def initiate_admin() -> None:
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        finance_repo = FinanceRepository(session)

        users = await user_repo.list()
        if users:
            return

        password_hash = SecurityHasher.get_password_hash(settings.ADMIN_PASSWORD)
        admin_data = {
            "username": settings.ADMIN_NAME,
            "email": settings.ADMIN_EMAIL,
            "password_hash": password_hash,
            "affiliate_code": settings.ADMIN_AFFILIATE_CODE,
            "is_admin": True,
            "is_active": True,
        }

        admin = UserSchema.model_validate(await user_repo.add(admin_data))
        await finance_repo.add({"user_id": admin.id, "balance": 10000000})
        await session.commit()
