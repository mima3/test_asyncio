import asyncio


async def maybe_cached(x):
    return x * 2  # await を含まない → eager なら即完了する


async def main():
    loop = asyncio.get_running_loop()  # 既存ループを取得
    loop.set_task_factory(asyncio.eager_task_factory)  # ★このループに設定
    try:
        t = asyncio.create_task(maybe_cached(21))
        assert t.done()  # ← eager なら True
        print(await t)  # 42
    finally:
        loop.set_task_factory(None)  # 片付け（元に戻す）


if __name__ == "__main__":
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
