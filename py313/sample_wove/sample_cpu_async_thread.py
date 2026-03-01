# async_threads_cpu_same_format.py  (Python 3.11+)
import math
import time
import asyncio
import os
import threading

# --- そのままの出力形式 ---
def count_primes(limit: int) -> int:
    print('start... count_primes', limit, os.getpid(), threading.get_ident())
    cnt = 0
    for n in range(2, limit):
        root = int(math.isqrt(n))
        for d in range(2, root + 1):
            if n % d == 0:
                break
        else:
            cnt += 1
    print('end... count_primes', limit, os.getpid(), threading.get_ident())
    return cnt

# スレッドに投げる（asyncで包む）
async def run_in_thread(func, *args):
    return await asyncio.to_thread(func, *args)

async def main():
    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(run_in_thread(count_primes, 800_000))
        t2 = tg.create_task(run_in_thread(count_primes, 900_000))
    elapsed = time.perf_counter() - start
    print(f"result1={t1.result()}, result2={t2.result()}")
    print(f"elapsed={elapsed:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
