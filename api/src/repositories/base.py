from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Sequence, Any
from redis.asyncio import Redis, ConnectionError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoSuchColumnError

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

    async def get_by_id(
        self, id: int, eager: Sequence[str] | None = None, for_update=False
    ) -> T | None:
        """Returns db object using :id

        Args:
            eager (sequence, optional): Sequence of fields that should be loaded eagerly. Defaults to [].
            for_update (bool): If True creates a lock for a record in the database

        Returns:
            T: Returns T record in db
        """
        stmt = select(self._model).filter_by(id=id)

        if eager:
            try:
                stmt = stmt.options(
                    joinedload(*[getattr(self._model, field) for field in eager])
                )
            except AttributeError:
                raise NoSuchColumnError("Non existent column in eager sequence")

        if for_update:
            stmt = stmt.with_for_update()

        return await self._session.scalar(stmt)

    async def get_by_filters(
        self, eager: Sequence[str] | None = None, for_update=False, **filters
    ) -> T | None:
        """Returns db object using :**filters

        Args:
            eager (sequence, optional): Sequence of fields that should be loaded eagerly. Defaults to [].
            for_update (bool): If True creates a lock for a record in the database
            **filters: Filters to filter out records

        Returns:
            T: Returns T record in db
        """
        stmt = select(self._model).filter_by(**filters)

        if eager:
            try:
                stmt = stmt.options(
                    joinedload(*[getattr(self._model, field) for field in eager])
                )
            except AttributeError:
                raise NoSuchColumnError("Non existent column in eager sequence")

        if for_update:
            stmt = stmt.with_for_update()

        return await self._session.scalar(stmt)

    async def list(self, eager: Sequence[str] | None = None, **filters) -> Sequence[T]:
        """Returns list of :T by :filters with fields :eager eager loaded

        Args:
            eager (sequence, optional): Sequence of fields that should be loaded eagerly. Defaults to [].
            **filters: Filters to filter out records
        Returns:
            Sequence[T]: Returns sequence of models T
        """
        stmt = select(self._model).filter_by(**filters)

        if eager:
            try:
                stmt = stmt.options(
                    joinedload(*[getattr(self._model, field) for field in eager])
                )
            except AttributeError:
                raise NoSuchColumnError("Non existent column in eager sequence")

        return (await self._session.scalars(stmt)).all()

    async def add(self, data: dict[str, Any]) -> T:
        """Adds a record with :data in database

        Args:
            data (dict[str, Any]): data for adding

        Returns:
            T: record object in database
        """
        record = self._model(**data)
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def update(self, id: int, data: dict[str, Any]) -> T | None:
        """Updates a record in database using :id

        Args:
            id (int): record ID in database
            data (dict[str, Any]): data for updating the record

        Returns:
            T | None: T model in database or None if data wasn't updated
        """
        data.pop("id", None)
        stmt = update(self._model).filter_by(id=id).values(data)
        await self._session.execute(stmt)
        await self._session.flush()
        record = await self.get_by_id(id=id)
        await self._session.refresh(record)
        return record

    async def delete(self, id: int) -> None:
        """Deletes a record in database using :id

        Args:
            id (int): id for a record in database
        """
        stmt = delete(self._model).filter_by(id=id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def is_exists(self, **filters) -> bool:
        """Checks if row exists

        Returns:
            bool: True or False
        """
        stmt = select(func.count()).select_from(self._model).filter_by(**filters)
        row_count = await self._session.scalar(stmt)
        if row_count:
            return True
        return False


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

    async def hset(self, name: Any, key: Any, value: Any) -> int | Any:
        if self._redis is None:
            raise ConnectionError("Redis connection had not be initialized")
        return await self._redis.hset(name, key, value)  # type: ignore

    async def hdel(self, name: Any, *keys: Any) -> int | Any:
        if self._redis is None:
            raise ConnectionError("Redis connection had not be initialized")
        return await self._redis.hdel(name, *keys)  # type: ignore

    async def sadd(self, name: Any, *values: Any) -> int | Any:
        if self._redis is None:
            raise ConnectionError("Redis connection had not be initialized")
        return await self._redis.sadd(name, *values)  # type: ignore

    async def srem(self, name: Any, *values: Any) -> int | Any:
        if self._redis is None:
            raise ConnectionError("Redis connection had not be initialized")
        return await self._redis.sadd(name, *values)  # type: ignore
