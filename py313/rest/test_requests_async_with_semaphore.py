import asyncio
import requests
import threading
from .data import get_url_list
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


_sessions_lock = threading.Lock()
_sessions: set[requests.Session] = set()
_local = threading.local()


def _get_session() -> requests.Session:
    """スレッド・ローカル変数にrequestsのセッションを登録しておき使い回す"""
    s = getattr(_local, "session", None)
    if s is None:
        s = requests.Session()
        with _sessions_lock:
            _sessions.add(s)
        _local.session = s
    return s


def close_all_sessions():
    """セッションを使い回しているのでクローズ処理をする"""
    with _sessions_lock:
        print("close requests session.", len(_sessions))
        for s in list(_sessions):
            try:
                s.close()
            finally:
                _sessions.discard(s)


def fetch_sync(url: str, timeout: float = 3.0):
    """同期の requests をそのまま使う関数（スレッドで実行される）"""
    print(f"  start fetch_sync.... thread_id:{threading.get_ident()}: {url}")
    try:
        res = _get_session().get(url, timeout=timeout)
        res.raise_for_status()
        ct = res.headers.get("content-type", "")
        body = res.json() if ct.startswith("application/json") else res.text
        return {"url": url, "success": True, "status": res.status_code, "body": body, "error": None}
    except requests.exceptions.ReadTimeout as e:
        return {"url": url, "success": False, "status": None, "body": None, "error": "timeout:" + str(e)}


async def fetch(url: str, sem: asyncio.Semaphore, timeout: float):
    async with sem:
        print(f"start fetch.... thread_id:{threading.get_ident()} {url}")
        # to_threadは内部でrun_in_executorを読んでいます。
        # ここでconcurrent.futures.ThreadPoolExecutorがでてきます。
        # これを確認するとmin(32, (os.process_cpu_count() or 1) + 4)のワーカースレッドを作っていることがわかります。
        # asyncio.to_threadで指定した関数は上記の空いているスレッドで動作します
        # https://github.com/python/cpython/blob/main/Lib/asyncio/threads.py
        # https://github.com/python/cpython/blob/main/Lib/asyncio/base_events.py#L884
        # https://github.com/python/cpython/blob/main/Lib/concurrent/futures/thread.py#L150
        return await asyncio.to_thread(fetch_sync, url, timeout)


async def main():
    print(f"start thread_id:{threading.get_ident()}")
    timeout = 3.0
    sem = asyncio.Semaphore(5)  # 同時実行上限（必要に応じて調整）

    try:
        tasks = []
        result = []
        async with asyncio.TaskGroup() as tg:
            for u in get_url_list():
                tasks.append(tg.create_task(fetch(u, sem, timeout)))
        for task in tasks:
            result.append(task.result())
    finally:
        close_all_sessions()

    for item in result:
        print(item)
    print("result...", len(result))


if __name__ == "__main__":
    install_profile_hooks()
    asyncio.run(main())
    uninstall_profile_hooks()
