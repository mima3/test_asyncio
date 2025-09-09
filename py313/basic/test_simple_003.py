import asyncio


async def test(name: str, n: float):
    print("start...", name)
    await asyncio.sleep(n)
    print("end...", name)
    return f"{name}:{n}"


async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(test("1番目", 2.5))
        task2 = tg.create_task(test("2番目", 1.5))
        task3 = tg.create_task(test("3番目", 3.0))
    print(task1.result())
    print(task2.result())
    print(task3.result())


if __name__ == "__main__":
    asyncio.run(main())
