import os
from contextlib import asynccontextmanager
from typing import Literal

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Default DSNs are aligned with docker-compose ports
PG_URL = os.getenv("PG_URL", "postgresql+asyncpg://app:app@localhost:5432/appdb")
MYSQL_URL = os.getenv("MYSQL_URL", "mysql+asyncmy://app:app@localhost:3306/appdb")


def make_engine(url: str) -> AsyncEngine:
    # echo=True to see SQL; set False to quiet
    return create_async_engine(url, echo=False, pool_pre_ping=True, future=True)


engine_pg: AsyncEngine = make_engine(PG_URL)
engine_mysql: AsyncEngine = make_engine(MYSQL_URL)

SessionPG = async_sessionmaker(engine_pg, expire_on_commit=False)
SessionMySQL = async_sessionmaker(engine_mysql, expire_on_commit=False)


def session_factory(db: Literal["pg", "mysql"] = "pg") -> async_sessionmaker[AsyncSession]:
    if db == "pg":
        return SessionPG
    elif db == "mysql":
        return SessionMySQL
    else:
        raise ValueError("db must be 'pg' or 'mysql'")


@asynccontextmanager
async def get_session(db: Literal["pg", "mysql"] = "pg"):
    factory = session_factory(db)
    async with factory() as session:
        yield session
