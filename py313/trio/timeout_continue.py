# https://trio.readthedocs.io/en/stable/reference-core.html#cancellation-and-timeouts
import trio

async def async_func(x):
    print('start .... async_func', x)
    await trio.sleep(x)
    print('end .... async_func')

async def main():
    print('start .... main')
    with trio.fail_after(2):
        await async_func(3)  # async_funcが完了する前に戻ってくる
    print('end .... main')

if __name__ == "__main__":
    trio.run(main)