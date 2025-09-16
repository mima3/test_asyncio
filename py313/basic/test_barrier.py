import asyncio
import random


async def worker(i: int, barrier: asyncio.Barrier):
    prep = random.uniform(0.05, 0.25)  # 準備時間はバラバラ
    await asyncio.sleep(prep)
    print(f"[W{i}] ready (prep {prep:.2f}s)")

    # 待機者が parties 人に達した瞬間に全員解除される
    pos = await barrier.wait()
    print(f"[W{i}] run...", pos)


async def main():
    parties = 5
    barrier = asyncio.Barrier(parties)
    async with asyncio.TaskGroup() as tg:
        for i in range(parties):
            tg.create_task(worker(i, barrier))


if __name__ == "__main__":
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
