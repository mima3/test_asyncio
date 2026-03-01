import trio


async def async_func(x):
    print('start .... async_func', x)
    await trio.sleep(x)
    print('end .... async_func', x)

async def parent():
    print("parent: started!")
    async with trio.open_nursery() as nursery:
        print("parent: spawning child1...")
        nursery.start_soon(async_func, 1)

        print("parent: spawning child2...")
        nursery.start_soon(async_func, 2)

        print("parent: waiting for children to finish...")
        # -- we exit the nursery block here --
    print("parent: all done!")

if __name__ == "__main__":
    print('start .... main')
    trio.run(parent)
    print('end .... main')
