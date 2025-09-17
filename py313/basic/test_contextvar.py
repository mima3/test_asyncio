import asyncio
from contextvars import ContextVar


request_id: ContextVar[str] = ContextVar("request_id", default="-")


async def proc(n: int):
    request_id.set(f"request_id:{n}")
    await asyncio.sleep(1)
    return request_id.get()


async def main():
    tasks = []
    async with asyncio.TaskGroup() as g:
        for i in range(10):
            tasks.append(g.create_task(proc(i)))
    for task in tasks:
        print(task.result())


if __name__ == "__main__":
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
