import asyncio
import time
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_session
from .models import User, Post
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


async def counts(session: AsyncSession, label: str):
    # Simple aggregate
    user_count = await session.scalar(select(func.count()).select_from(User))
    post_count = await session.scalar(select(func.count()).select_from(Post))
    print(f"[{label}] users={user_count}, posts={post_count}")


async def show_posts(session: AsyncSession, label: str):
    stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
    users = await session.stream_scalars(stmt)
    async for u in users:
        print(f"[{label}] User #{u.id} {u.name}")
        for p in u.posts:
            print(f"  └─ ({p.id}) title:{p.title} body:{p.body}")


async def add_ok(session: AsyncSession, db_label: str):
    """正常の追加処理"""
    print(f"[{db_label}] add_ok...")
    prefix = f"OK:{str(time.time())[-3:]}"
    # Create a user + 2 posts
    try:
        async with session.begin():
            u = User(name=f"{db_label} {prefix} User")
            session.add(u)
            await session.flush()  # populate u.id

            session.add_all(
                [
                    Post(user_id=u.id, title="Hello", body=f"Hello from {db_label}! {prefix}"),
                    Post(user_id=u.id, title="Async ORM", body=f"Async demo on {db_label} {prefix}"),
                ]
            )
            await session.commit()
            print(f"[{db_label}] add_ok User(id={u.id}).")
    except Exception as e:
        print("add_ok 例外が発生....", e)


async def add_ng(session: AsyncSession, db_label: str):
    """ロールバックを発生させる追加"""
    print(f"[{db_label}] add_ng...")
    prefix = f"NG:{str(time.time())[-3:]}"
    # Create a user + 2 posts
    try:
        async with session.begin():
            u = User(name=f"{db_label} {prefix} User")
            session.add(u)
            await session.flush()  # populate u.id

            session.add_all(
                [
                    Post(user_id=u.id, title="Hello", body=f"Hello from {db_label}! {prefix}"),
                    Post(user_id=u.id, title="Async ORM", body=f"Async demo on {db_label} {prefix}"),
                ]
            )
            raise RuntimeError("Force rollback")
    except Exception as e:
        print("***********add_ng 例外が発生....", e)


async def run_for(db_label: str):
    async with get_session("pg" if db_label == "PostgreSQL" else "mysql") as session:
        # session.begin()でselectとかやると暗黙的にsession.begin()が実行されてしまう
        async with session.begin():
            await counts(session, db_label)
            await show_posts(session, db_label)

        print("......追加OK")
        await add_ok(session, db_label)
        print("......追加NG")
        await add_ng(session, db_label)

        print("......追加後")
        async with session.begin():
            await counts(session, db_label)
            await show_posts(session, db_label)


async def main():
    # Run both DBs concurrently to demonstrate asyncio usage
    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_for("PostgreSQL"))
        tg.create_task(run_for("MySQL"))


if __name__ == "__main__":
    install_profile_hooks()
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
    uninstall_profile_hooks()
