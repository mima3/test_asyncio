import asyncio
import time

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def dummy_sleep(n):
    print("dummy_sleep... start", n)
    await asyncio.sleep(1)
    print("dummy_sleep... end")
    return n * 10


async def test_async_print(name):
    print("start...")
    await dummy_sleep(0.5)
    print("dummy_sleep(0.5) end")
    await dummy_sleep(0.8)
    print("dummy_sleep(0.8) end")
    return "hogehoge"


def main():
    print("main...")
    coroutine = test_async_print("abc")

    def send(coro):
        result = coro.send(None)
        print("coro result:", result)
        blocking = getattr(result, "_asyncio_future_blocking", None)
        print("   _state:", result._state)
        print("   blocking:", blocking)
        if blocking:
            result.set_result(None)
            time.sleep(1)
            # asyncio.futures.future_add_to_awaited_by(result,)
            # result._asyncio_future_blocking = False
            # result.add_done_callback(callback_feature)

    while True:
        try:
            send(coroutine)
        except StopIteration as e:
            print(e)
            break


loop.call_soon(main)
loop.call_later(5, loop.stop)
loop.run_forever()
loop.close()
