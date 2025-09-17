# bench_uvloop_echo.py
import asyncio
import time
import uvloop
from dataclasses import dataclass

# 測定パラメータ（環境に合わせて増減）
CONNECTIONS = 200  # 同時接続数
MSGS_PER_CONN = 200  # 1接続あたりの往復回数
PAYLOAD_SIZE = 1024  # 1メッセージのバイト数


@dataclass
class Result:
    label: str
    seconds: float
    bytes_total: int


async def _echo_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    finally:
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()


async def _start_server():
    server = await asyncio.start_server(_echo_handler, "127.0.0.1", 0, backlog=1024)
    addr = server.sockets[0].getsockname()
    return server, addr  # addr = (host, port)


async def _run_clients(addr, connections, msgs_per_conn, payload_size):
    payload = b"x" * payload_size

    async def one_client():
        reader, writer = await asyncio.open_connection(*addr)
        try:
            for _ in range(msgs_per_conn):
                writer.write(payload)
                await writer.drain()
                # エコーバックを同サイズぶん受信
                await reader.readexactly(payload_size)
        finally:
            writer.close()
            await writer.wait_closed()

    await asyncio.gather(*(one_client() for _ in range(connections)))


async def _bench_once(label: str) -> Result:
    # サーバ起動
    server, addr = await _start_server()
    try:
        # 実測
        t0 = time.perf_counter()
        await _run_clients(addr, CONNECTIONS, MSGS_PER_CONN, PAYLOAD_SIZE)
        dt = time.perf_counter() - t0
    finally:
        server.close()
        await server.wait_closed()

    # 往復ぶん(送受信で2倍)の総バイト数
    total_bytes = CONNECTIONS * MSGS_PER_CONN * PAYLOAD_SIZE * 2
    return Result(label, dt, total_bytes)


def _set_loop_policy(policy: str):
    if policy == "uvloop":
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    else:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())


async def main():
    # ウォームアップ（標準ループで軽く動かす）
    await _bench_once("warmup")

    # 標準ループ
    r1 = await _bench_once("stdlib")

    # uvloop（あれば）
    try:
        _set_loop_policy("uvloop")
        # 新しいポリシーで改めて run
        r2 = await asyncio.get_running_loop().run_in_executor(
            None, lambda: asyncio.run(_bench_once("uvloop"))  # スレッドでサブプロセスを起こさない簡易手
        )
    except ModuleNotFoundError:
        r2 = None

    # 結果表示
    def show(res: Result):
        mb = res.bytes_total / (1024 * 1024)
        thr_mb_s = mb / res.seconds
        ops = (CONNECTIONS * MSGS_PER_CONN) / res.seconds
        print(f"[{res.label}] {res.seconds:.3f}s  | {thr_mb_s:.2f} MiB/s | {ops:.0f} msg/s")

    show(r1)
    if r2:
        show(r2)
        speedup = r1.seconds / r2.seconds
        print(f"speedup (stdlib → uvloop): x{speedup:.2f}")
    else:
        print("uvloop が見つかりませんでした。`pip install uvloop` を実行してください。")


if __name__ == "__main__":
    import contextlib

    # 標準ループで開始
    _set_loop_policy("stdlib")
    asyncio.run(main())
