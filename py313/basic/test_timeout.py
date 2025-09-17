import asyncio


async def main():
    try:
        print("start. wait_for")
        await asyncio.wait_for(asyncio.sleep(5), 1)
    except asyncio.TimeoutError:
        print("  wait_for...")
    try:
        print("start. timeout")
        async with asyncio.timeout(1):
            await asyncio.sleep(5)
    except asyncio.TimeoutError:
        print("  timeout...")

    try:
        print("start. timeout_at")
        deadline = asyncio.get_running_loop().time() + 1
        async with asyncio.timeout_at(deadline):
            await asyncio.sleep(5)
    except asyncio.TimeoutError:
        print("  timeout_at...")


if __name__ == "__main__":
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
