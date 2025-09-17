import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, select


from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

# PostgresSQLの場合
# DB_URL = "postgresql+asyncpg://app:app@localhost:5432/appdb"
# MySQL + asyncmyの場合
DB_URL = "mysql+asyncmy://app:app@localhost:3306/appdb"
# MySQL + aiomysql: RuntimeError: Event loop is closedでエラー
# DB_URL = "mysql+aiomysql://app:app@localhost:3306/appdb"


def make_engine(url: str) -> AsyncEngine:
    # echo=True to see SQL; set False to quiet
    return create_async_engine(url, echo=False, pool_pre_ping=True, future=True)


engine_db: AsyncEngine = make_engine(DB_URL)
SessionDB = async_sessionmaker(engine_db, expire_on_commit=False)


@asynccontextmanager
async def get_session():
    async with SessionDB() as session:
        yield session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"User(id={self.id!r}, name={self.name!r})"


async def main():
    async with get_session() as session:
        async with session.begin():
            stmt = select(User).order_by(User.id)
            users = await session.stream_scalars(stmt)
            async for u in users:
                print(f"[User] #{u.id} {u.name}")


with asyncio.Runner(debug=True) as runner:
    runner.run(main())
