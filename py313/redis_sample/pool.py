import asyncio
from datetime import datetime
import redis.asyncio as redis
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


async def write(idx: int, r: redis.Redis):
    # r.setの時点でコネクションプールからコネクションを借りて終わったら返す
    print("  write start", idx)
    await r.set(f"data_{idx}", str(datetime.now()))
    # dummy
    await asyncio.sleep(1)
    print("  write end", idx)


async def read(idx: int, r: redis.Redis):
    # r.setの時点でコネクションプールからコネクションを借りて終わったら返す
    print("  read start", idx)
    res = await r.get(f"data_{idx}")
    await asyncio.sleep(1)
    print("  read end", idx)
    return res


async def main():
    MAX_CNT = 50
    pool = redis.BlockingConnectionPool.from_url("redis://localhost:6379/0", max_connections=5, timeout=10)
    async with redis.Redis(connection_pool=pool) as r:
        w_tasks = []
        r_tasks = []
        print("start... write")
        async with asyncio.TaskGroup() as tg:
            for i in range(MAX_CNT):
                w_tasks.append(tg.create_task(write(i, r)))
        print("start... read")
        async with asyncio.TaskGroup() as tg:
            for i in range(MAX_CNT):
                r_tasks.append(tg.create_task(read(i, r)))
        print("taskの結果")
        for task in r_tasks:
            print(task.result())


if __name__ == "__main__":
    install_profile_hooks()
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
    uninstall_profile_hooks()
