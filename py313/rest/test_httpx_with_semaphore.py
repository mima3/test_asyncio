import asyncio
import httpx
import threading
from .data import get_url_list
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


async def fetch(client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore):
    async with sem:
        try:
            print(f"start get.... thread_id:{threading.get_ident()} {url}")
            r = await client.get(url)  # タイムアウトはここで発生
            r.raise_for_status()  # 4xx/5xx を例外化
            body = r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
            return {"url": url, "success": True, "status": r.status_code, "body": body, "error": None}

        except httpx.TimeoutException as e:
            # ← タイムアウトだったことが呼び出し側で判別できる
            return {"url": url, "success": False, "status": None, "body": None, "error": "timeout:" + str(e)}

        except httpx.HTTPStatusError as e:
            # 4xx/5xx（raise_for_status による）
            return {
                "url": url,
                "success": False,
                "status": e.response.status_code,
                "body": e.response.text,
                "error": "http_status_error:" + str(e),
            }

        except httpx.RequestError as e:
            # DNS失敗/接続失敗などのネットワーク系
            return {"url": url, "success": False, "status": None, "body": None, "error": "request_error:" + str(e)}


async def main():
    print(f"start thread_id:{threading.get_ident()}")
    limits = httpx.Limits(max_connections=20, max_keepalive_connections=20)
    timeout = httpx.Timeout(3.0)
    sem = asyncio.Semaphore(5)  # 同時実行上限（必要に応じて調整）

    result = []
    async with httpx.AsyncClient(http2=False, timeout=timeout, limits=limits) as client:
        tasks = [asyncio.create_task(fetch(client, u, sem)) for u in get_url_list()]
        for item in await asyncio.gather(*tasks):
            result.append(item)

    for item in result:
        print(item)
    print("result...", len(result))


if __name__ == "__main__":
    install_profile_hooks()
    asyncio.run(main())
    uninstall_profile_hooks()
