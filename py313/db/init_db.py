import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from .db import engine_pg, engine_mysql, get_session
from .models import Base, User, Post
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


async def create_all(engine: AsyncEngine, label: str):
    async with engine.begin() as conn:
        print(f"Creating tables on {label}...")
        await conn.run_sync(Base.metadata.create_all)
        print(f"Done on {label}.")


async def make_init_data(db_label: str):
    print(f"[{db_label}] make_init_data...")
    async with get_session("pg" if db_label == "PostgreSQL" else "mysql") as session:
        # Create a user + 2 posts
        u = User(name=f"{db_label} User")
        session.add(u)
        await session.flush()  # populate u.id

        session.add_all(
            [
                Post(user_id=u.id, title="Hello", body=f"Hello from {db_label}!"),
                Post(user_id=u.id, title="Async ORM", body=f"Async demo on {db_label}"),
            ]
        )
        await session.commit()
    print(f"[{db_label}] make_init_data User(id={u.id}).")


async def main():
    await asyncio.gather(
        create_all(engine_pg, "PostgreSQL"),
        create_all(engine_mysql, "MySQL"),
    )
    await asyncio.gather(
        make_init_data("PostgreSQL"),
        make_init_data("MySQL"),
    )


if __name__ == "__main__":
    install_profile_hooks()
    asyncio.run(main())
    uninstall_profile_hooks()
