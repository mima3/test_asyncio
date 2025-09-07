import asyncio
from .db import engine_pg, engine_mysql
from .models import Base


def child_first_table_names() -> list[str]:
    # 外部キー依存の逆順（= 子→親）
    return [t.name for t in reversed(list(Base.metadata.sorted_tables))]


async def truncate_postgres():
    names = child_first_table_names() or ["posts", "users"]
    print("[PostgreSQL] TRUNCATE 開始: ", names)
    # まとめて TRUNCATE（ID リセット＆カスケード）
    stmt = f"TRUNCATE TABLE {', '.join(names)} RESTART IDENTITY CASCADE;"
    async with engine_pg.begin() as conn:
        await conn.exec_driver_sql(stmt)
    print("[PostgreSQL] TRUNCATE 完了: ", names)


async def truncate_mysql():
    names = child_first_table_names() or ["posts", "users"]
    print("[MySQL] TRUNCATE 開始: ", names)
    async with engine_mysql.begin() as conn:
        # FK制約を一時無効化して順に TRUNCATE
        try:
            await conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 0;")
            for tbl in names:
                await conn.exec_driver_sql(f"TRUNCATE TABLE `{tbl}`;")
        finally:
            # 念のため再有効化（例外時も戻す）
            try:
                await conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 1;")
            except Exception:
                pass
    print("[MySQL] TRUNCATE 完了: ", names, "（AUTO_INCREMENTもリセット）")


async def main():
    # 並列に実行
    await asyncio.gather(truncate_postgres(), truncate_mysql())


if __name__ == "__main__":
    asyncio.run(main())
