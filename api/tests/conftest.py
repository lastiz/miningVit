# import pytest
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# from sqlalchemy.pool import NullPool

# from src.database.db import DB
# from src.database.models import Base
# from src.main import app
# from src.config import settings


# DATABASE_URL_TEST = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_TCP_PORT}/{settings.MYSQL_DATABASE}"
# engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
# async_session_maker = async_sessionmaker(
#     bind=engine_test,
#     expire_on_commit=False,
#     autoflush=False,
#     autocommit=False,
# )
