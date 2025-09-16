import asyncio
from typing import Optional, Any

"""
TaskGroup vs gather

- タスクの寿命をスコープで閉じたい／失敗時に兄弟タスクを確実に畳みたい → TaskGroup
- 単に N 個の awaitable を並行実行して結果リストが欲しい → gather
- 複数同時失敗を正しく扱いたい（集約して上げたい） → TaskGroup（ExceptionGroup）
- 例外も“値”として扱いたい（失敗しても進めたい） → gather(return_exceptions=True)
- 3.10 以前でも動かしたい → gather
- グループをネストさせたい → TaskGroup
"""


async def ok(name: str, delay: float):
    print(f"{name}: start")
    await asyncio.sleep(delay)
    print(f"{name}: done")
    return f"{name}-result"


async def boom(name: str, delay: float):
    print(f"{name}: start")
    await asyncio.sleep(delay)
    print(f"{name}: about to raise")
    raise ValueError(f"{name} failed")


async def sleepy(name: str, delay: float):
    try:
        print(f"{name}: start")
        await asyncio.sleep(delay)
        print(f"{name}: done")
        return f"{name}-result"
    except asyncio.CancelledError:
        print(f"{name}: CancelledError")
        raise


# 1) TaskGroup（成功時）：結果の取り方
async def demo_taskgroup_success():
    print("\n--- demo_taskgroup_success ---")
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(ok("A", 0.30))
        t2 = tg.create_task(ok("B", 0.10))
        t3 = tg.create_task(ok("C", 0.20))
    # ここまで来たら全タスク完了済み。各 Task から result() で回収する
    print("results:", t1.result(), t2.result(), t3.result())


# 2) gather（成功時）：リストで返る
async def demo_gather_success():
    print("\n--- demo_gather_success ---")
    results = await asyncio.gather(ok("A", 0.30), ok("B", 0.10), ok("C", 0.20))
    print("results:", results)


# 3) TaskGroup（失敗時）：兄弟はキャンセルされ、例外は ExceptionGroup で再送出
async def demo_taskgroup_failure():
    print("\n--- demo_taskgroup_failure ---")
    t_ok: Optional[asyncio.Task[str]] = None
    t_bad: Optional[asyncio.Task[Any]] = None
    t_slow: Optional[asyncio.Task[str]] = None
    t_slow2: Optional[asyncio.Task[str]] = None
    try:
        async with asyncio.TaskGroup() as tg:
            t_ok = tg.create_task(ok("OK", 0.1))
            t_bad = tg.create_task(boom("BAD", 0.20))
            t_slow = tg.create_task(sleepy("SLOW", 2.00))  # 巻き添えでキャンセルされる
            t_slow2 = tg.create_task(sleepy("SLOW2", 2.00))  # 同上
    except* ValueError as eg:
        print("TaskGroup raised:", eg)
        # t_bad は ValueError、SLOW/SLOW2 は Cancelled（通常 ExceptionGroup には含められない）
        if t_ok:
            print("t_ok", t_ok.result())
        if t_bad:
            print("t_bad.done?      ", t_bad.done(), "exc:", type(t_bad.exception()).__name__)
        if t_slow:
            print("t_slow.cancelled?", t_slow.cancelled())
        if t_slow2:
            print("t_slow2.cancelled?", t_slow2.cancelled())


# 4) gather（失敗時・デフォルト）：最初の例外だけを上げ、他をキャンセル
async def demo_gather_failure_default():
    print("\n--- demo_gather_failure_default ---")
    try:
        res = await asyncio.gather(
            ok("OK", 0.1),
            boom("BAD", 0.20),
            sleepy("SLOW", 2.00),  # キャンセルされない
            sleepy("SLOW2", 2.00),  # キャンセルされない
        )
        # 実行されないはず
        print("demo_gather_failure_default result:", res)
    except Exception as e:
        print("gather raised:", type(e).__name__, e)
    print("--------------------- asyncio.gatherが終わったあとの実行")
    await asyncio.sleep(3.0)
    print("-----------------------------------------------------")


# 5) gather（return_exceptions=True）：例外を結果として返し、基本キャンセルしない
async def demo_gather_return_exceptions():
    print("\n--- demo_gather_return_exceptions ---")
    results = await asyncio.gather(
        ok("OK", 0.1),
        boom("BAD", 0.20),  # ValueError が「結果」として返る
        sleepy("SLOW", 0.30),
        ok("OK", 0.10),
        return_exceptions=True,
    )
    # 表示を見やすく
    norm = [(type(x).__name__ if isinstance(x, BaseException) else x) for x in results]
    print("results:", norm)


# 6) TaskGroupのネストの確認
async def demo_taskgroup_nest():
    print("\n--- demo_taskgroup_nest ---")

    async def make_groupA():
        print("start---- make_groupA")
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(ok("A1", 1.00))
            t2 = tg.create_task(ok("A2", 2.00))
        print("end---- make_groupA")
        return (t1.result(), t2.result())

    async def make_groupB():
        print("end---- make_groupB")
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(ok("B1", 1.30))
            t2 = tg.create_task(ok("B2", 1.00))
            t3 = tg.create_task(ok("B3", 1.10))
        print("end---- make_groupB")
        return (t1.result(), t2.result(), t3.result())

    async with asyncio.TaskGroup() as outer_group:
        g1 = outer_group.create_task(make_groupA())
        g2 = outer_group.create_task(make_groupB())
    print(g1.result())
    print(g2.result())


async def main():
    await demo_taskgroup_success()
    await demo_taskgroup_nest()
    await demo_gather_success()
    await demo_taskgroup_failure()
    await demo_gather_return_exceptions()
    await demo_gather_failure_default()


if __name__ == "__main__":
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
