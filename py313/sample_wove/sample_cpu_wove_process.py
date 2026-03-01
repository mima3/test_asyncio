# sample_cpu_wove.py  (Python 3.11+ / 3.13 / 3.14)
import math
import time
import os
import threading
from wove import weave  # pip install wove

# --- CPUバウンドな処理（素朴な素数カウント） ---
def count_primes(limit: int) -> int:
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
    elapsed = time.perf_counter() - start
    print('end... count_primes', limit, elapsed, os.getpid(), threading.get_ident(), flush=True)
    return cnt

def main():
    start = time.perf_counter()
    print('main.', os.getpid())

    with weave(fork=True) as w:
        # 2つのCPU仕事を“同時に”投げる（タスクは順不同で実行される）
        @w.do
        def primes_800k():
            return count_primes(800_000)

        @w.do
        def primes_900k():
            return 1
            # return count_primes(900_000)

        # 依存タスク（両方の結果が揃ってから実行）
        @w.do
        def finalize(primes_800k, primes_900k):
            return primes_800k, primes_900k

    # weave ブロック終了時に全タスク完了。結果は w.result から取得
    r1, r2 = w.result.final  # finalize の戻り値
    elapsed = time.perf_counter() - start
    print(f"result1={r1}, result2={r2}")
    print(f"elapsed={elapsed:.2f}s")

if __name__ == "__main__":
    main()
