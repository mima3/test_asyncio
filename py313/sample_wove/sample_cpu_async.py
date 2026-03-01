# pure_async_cpu_cooperative.py  (Python 3.11+)
import math
import time
import asyncio
import os
import threading

# --- 純粋 async での CPU 処理（並行：協調的に切替） ---
async def count_primes_async(limit: int) -> int:
    print('start... count_primes', limit, os.getpid(), threading.get_ident())
    cnt = 0
    for n in range(2, limit):
        root = int(math.isqrt(n))
        for d in range(2, root + 1):
            if n % d == 0:
                break
        else:
            cnt += 1
        # たまにイベントループへ制御を返す（協調的並行）もできる
        # if (n & 1000) == 0:  # 8192回ごと
        #    await asyncio.sleep(0)
    print('end... count_primes', limit, os.getpid(), threading.get_ident())
    return cnt

async def main():
    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(count_primes_async(800_000))
        t2 = tg.create_task(count_primes_async(900_000))
    elapsed = time.perf_counter() - start
    print(f"result1={t1.result()}, result2={t2.result()}")
    print(f"elapsed={elapsed:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
