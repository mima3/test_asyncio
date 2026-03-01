import trio


async def producer(work_send: trio.MemorySendChannel[int], n: int) -> None:
    async with work_send:
        for i in range(n):
            print(f"[producer] sending work {i}")
            await work_send.send(i)
            print(f"[producer] sent work {i}")


async def worker(
    work_recv: trio.MemoryReceiveChannel[int],
    result_send: trio.MemorySendChannel[str],
) -> None:
    async with work_recv, result_send:
        async for x in work_recv:
            # 何か処理した体にする
            print(f"  [worker] start {x}")
            await trio.sleep(0.1)
            msg = f"work {x} -> result {x * x}"
            print(f"  [worker] sending {x}")
            await result_send.send(msg)
            print(f"  [worker] processed {x}")


async def consumer(result_recv: trio.MemoryReceiveChannel[str]) -> None:
    async with result_recv:
        async for msg in result_recv:
            print(f"    [consumer] got start: {msg}")
            await trio.sleep(0.1)
            print(f"    [consumer] got end: {msg}")


async def main() -> None:
    # 仕事チャンネル（producer -> worker）
    work_send, work_recv = trio.open_memory_channel(0)  # 0は同期チャネル（バッファなし）

    # 結果チャンネル（worker -> consumer）
    result_send, result_recv = trio.open_memory_channel(2)  # こっちは少しバッファあり

    async with trio.open_nursery() as nursery:
        nursery.start_soon(producer, work_send, 5)
        nursery.start_soon(worker, work_recv, result_send)
        nursery.start_soon(consumer, result_recv)
        # producer が work_send を閉じる → worker の async for が終わる → worker が result_send を閉じる
        # → consumer の async for も終わって全タスク自然終了


if __name__ == "__main__":
    trio.run(main)
