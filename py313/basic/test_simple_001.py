import asyncio


async def test(name: str, n: float):
    print("start...", name)
    await asyncio.sleep(n)
    print("end...", name)
    return f"{name}:{n}"


async def main():
    res1 = await test("1番目", 2.5)
    res2 = await test("2番目", 1.5)
    res3 = await test("3番目", 3.0)
    print(res1)
    print(res2)
    print(res3)


if __name__ == "__main__":
    asyncio.run(main())
