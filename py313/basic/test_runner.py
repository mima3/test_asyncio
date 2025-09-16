import asyncio


async def test(name: str, n: float):
    print("start...", name)
    await asyncio.sleep(n)
    print("end...", name)
    return f"{name}:{n}"


async def main1():
    await test("1番目", 0.5)
    await test("2番目", 2.5)  # 同じループ・同じContextVarsで続けて実行


def main2():
    with asyncio.Runner(debug=True) as runner:
        runner.run(test("1番目", 0.5))
        runner.run(test("2番目", 2.5))  # 同じループ・同じContextVarsで続けて実行


if __name__ == "__main__":
    # 古い書き方
    asyncio.run(main1())
    main2()
