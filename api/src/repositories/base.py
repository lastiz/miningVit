from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Sequence, Never, Any
from redis.asyncio import Redis, ConnectionError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from database.models import Base
from config import settings


T = TypeVar("T", bound=Base)


class GenericRepository(Generic[T], ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> T | None:
        raise NotImplementedError()

    @abstractmethod
    def list(self, **filters) -> list[T]:
        raise NotImplementedError()

    @abstractmethod
    def add(self, record: dict) -> T:
        raise NotImplementedError()

    @abstractmethod
    def update(self, record: dict) -> T:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, id: int) -> None:
        raise NotImplementedError()


class GenericSqlRepository(GenericRepository[T], ABC):
    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        self._session = session
        self._model = model

    async def get_by_id(self, id: int) -> T | None:
        stmt = select(self._model).filter_by(id=id)
        return await self._session.scalar(stmt)

    async def get_by_id_for_update(self, id: int) -> T | None:
        stmt = select(self._model).filter_by(id=id).with_for_update()
        return await self._session.scalar(stmt)

    async def list(self, **filters) -> Sequence[T] | Sequence[Never]:
        stmt = select(self._model).filter_by(**filters)
        return (await self._session.scalars(stmt)).all()

    async def add(self, data: dict[str, Any]) -> T:
        record = self._model(**data)
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def update(self, id: int, data: dict[str, Any]) -> T | None:
        data.pop("id", None)
        stmt = update(self._model).filter_by(id=id).values(data)
        await self._session.execute(stmt)
        await self._session.flush()
        record = await self.get_by_id(id=id)
        return record

    async def delete(self, id: int) -> None:
        stmt = delete(self._model).filter_by(id=id)
        await self._session.execute(stmt)
        await self._session.flush()


class GenreicRedisRepository(ABC):
    def __init__(self) -> None:
        self._redis: Redis | None

    async def init(self) -> None:
        self._redis = await Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,
        )

    async def close(self) -> None:
        if self._redis is None:
            raise ConnectionError("Redis connection had not be initialized")
        await self._redis.aclose()

    async def get(self, key: Any) -> Any | None:
        if self._redis is None:
            raise ConnectionError("Redis connection had not be initialized")
        return await self._redis.get(key)

    async def set(self, key: Any, value: Any, expire: int | None) -> bool:
        if self._redis is None:
            raise ConnectionError("Redis connection had not be initialized")
        return await self._redis.set(key, value, ex=expire)

    async def delete(self, key: Any) -> bool:
        if self._redis is None:
            raise ConnectionError("Redis connection had not be initialized")
        return await self._redis.delete(key)
