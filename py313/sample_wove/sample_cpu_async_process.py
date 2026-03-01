# pip install aiomultiprocess
import asyncio, os, threading, math, time
from aiomultiprocess import Pool
from asyncio import gather, sleep

async def count_primes(limit: int) -> int:
    start = time.perf_counter()
    print('start... count_primes', limit, os.getpid(), threading.get_ident(), flush=True)
    cnt = 0
    for n in range(2, limit):
        root = int(math.isqrt(n))
        for d in range(2, root + 1):
            if n % d == 0:
                break
        else:
            cnt += 1
    print('end... count_primes', limit, time.perf_counter() - start, os.getpid(), threading.get_ident(), flush=True)
    return cnt

async def main():
    async with Pool(processes=2, childconcurrency=1) as pool:
        result = await gather(
            pool.apply(count_primes, args=(800_000,)),
            pool.apply(count_primes, args=(800_000,))
        )
        print(f"result1={result}")

if __name__ == "__main__":
    asyncio.run(main())