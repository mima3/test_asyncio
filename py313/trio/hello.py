import trio

async def async_func(x):
    print('start .... async_func', x)
    await trio.sleep(x)
    print('end .... async_func')

print('start .... main')
trio.run(async_func, 1)
print('end .... main')
