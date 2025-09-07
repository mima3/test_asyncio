import time
import requests
import threading
from data import get_url_list


def fetch_sync(url: str, timeout: float = 3.0):
    """同期の requests をそのまま使う関数（スレッドで実行される）"""
    print(f"start get sync.... thread_id:{threading.get_ident()}: {url}")
    try:
        res = requests.get(url, timeout=timeout)
        res.raise_for_status()
        ct = res.headers.get("content-type", "")
        body = res.json() if ct.startswith("application/json") else res.text
        return {"url": url, "success": True, "status": res.status_code, "body": body, "error": None}
    except requests.exceptions.ReadTimeout as e:
        return {"url": url, "success": False, "status": None, "body": None, "error": "timeout:" + str(e)}


def main():
    print(f"start thread_id:{threading.get_ident()}")
    t0 = time.perf_counter()
    result = []
    for url in get_url_list():
        res = fetch_sync(url, 3.0)
        result.append(res)
    for item in result:
        print(item)
    print("result...", len(result))
    print(f"done in {time.perf_counter() - t0:.3f}s")


if __name__ == "__main__":
    main()
