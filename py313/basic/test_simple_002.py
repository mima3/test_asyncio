import asyncio


async def test(name: str, n: float):
    print("start...", name)
    await asyncio.sleep(n)
    print("end...", name)
    return f"{name}:{n}"


async def main():
    result = await asyncio.gather(
        test("1番目", 2.5),
        test("2番目", 1.5),
        test("3番目", 3.0),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
