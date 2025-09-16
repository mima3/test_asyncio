import asyncio
import sys
from typing import Optional
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


async def run_and_stream(name: str, cmd: list[str], timeout: float | None = None) -> Optional[int]:
    """
    サブプロセスを起動し、stdout/stderr を行単位で非同期に読み出して表示。
    timeout 秒で終了しなければ terminate→kill。
    戻り値はプロセスの returncode。
    """
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    async def pipe_reader(stream: asyncio.StreamReader, label: str):
        while True:
            line = await stream.readline()
            if not line:
                break
            print(f"{label} {line.decode(errors='replace').rstrip()}")

    done = asyncio.Event()  # プロセス終了通知

    async def wait_proc():
        await proc.wait()
        done.set()

    async def timeout_guard():
        # timeout までに終了しなければ terminate→kill
        try:
            await asyncio.wait_for(done.wait(), timeout)
        except asyncio.TimeoutError:
            if proc.returncode is None:
                proc.terminate()
                try:
                    await asyncio.wait_for(done.wait(), 5)
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
            done.set()

    stdout = proc.stdout
    stderr = proc.stderr
    if stdout is None or stderr is None:
        # PIPEを指定している限り実行時には到達しない想定だが、型を満たすためにガード
        raise RuntimeError("stdout/stderr pipe is not available")

    # --- TaskGroupで寿命をスコープに閉じ込める ---
    async with asyncio.TaskGroup() as tg:
        tg.create_task(pipe_reader(stdout, f"{name} [OUT]"))
        tg.create_task(pipe_reader(stderr, f"{name} [ERR]"))
        tg.create_task(wait_proc())
        if timeout is not None:
            tg.create_task(timeout_guard())
    # ここに来た時点で上のタスク群は必ず完了
    return proc.returncode


async def main():
    # 例: “Python自身”を子プロセスとして起動してメッセージを出させる
    code1 = """
import time
from datetime import datetime
for i in range(5):
    print(f'A {i} {datetime.now()}', flush=True)
    time.sleep(0.5)
raise "Error A"
"""
    code2 = """
import time
from datetime import datetime
for i in range(5):
    print(f'B {i} {datetime.now()}', flush=True)
    time.sleep(1.0)
"""
    cmds = [
        ("processA", [sys.executable, "-u", "-c", code1]),
        ("processB", [sys.executable, "-u", "-c", code2]),
    ]

    # 並行に2つの子プロセスを実行（それぞれ3秒タイムアウト）
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(run_and_stream(name, cmd, timeout=10.0)) for name, cmd in cmds]
    for item, task in zip(cmds, tasks):
        print(item[0], task.result())


if __name__ == "__main__":
    install_profile_hooks()
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
    uninstall_profile_hooks()
