import asyncio
from datetime import datetime, timezone


"""
async def test_async_print(name, n):
    print(name, f"start....1: {n}")
    # await asyncio_copy.sleep(n)
    #await asyncio_copy.sleep(n)  # ポイント1 停止・別タスクを実行可能
    #print(name, f"start....2: {n}")
    #await asyncio_copy.sleep(n)  # ポイント2 停止・別タスクを実行可能
    #print(name, f"start....3: C{n}")
    #await asyncio_copy.sleep(n)  # ポイント3 停止・別タスクを実行可能
    #print(name, "end")
    #return "test_async_print_" + name

async def main():
    await test_async_print("test", 1)
    #await asyncio_copy.gather(
    #    test_async_print('CoA', 1.0),
    #    test_async_print('CoB', 0.5),
    #    test_async_print('CoC', 2.0)
    #)

asyncio_copy.run(main(), debug=True)"
"""


def test_print(name):
    print(datetime.now(), name)


loop = asyncio.new_event_loop()

ts = datetime.now(timezone.utc).timestamp()

test_print("スケジュールには積まない")
loop.call_soon(test_print, "即時実行1つ目")
loop.call_later(1.0, test_print, "1秒後 1つ目")
loop.call_later(1.0, test_print, "1秒後 2つ目")
loop.call_soon(test_print, "即時実行 2つ目")
loop.call_later(1.5, test_print, "1.5秒後")
loop.call_at(loop.time() + 3.0, test_print, "3秒後")
loop.call_later(5, loop.stop)
loop.run_forever()
loop.close()
