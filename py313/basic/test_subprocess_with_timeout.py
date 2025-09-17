import asyncio
import sys
from typing import Sequence
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


async def run_and_stream(name: str, cmd: Sequence[str], timeout: float) -> int:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = proc.stdout, proc.stderr
    if stdout is None or stderr is None:
        raise RuntimeError("stdout/stderr pipe is not available")

    async def pipe_reader(stream: asyncio.StreamReader, label: str):
        while True:
            line = await stream.readline()
            if not line:
                break
            print(f"{label} {line.decode(errors='replace').rstrip()}")

    try:
        async with asyncio.timeout(timeout):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(pipe_reader(stdout, f"{name} [OUT]"))
                tg.create_task(pipe_reader(stderr, f"{name} [ERR]"))
                # 子プロセス終了を待つ（正常終了時はここを抜ける）
                await proc.wait()
        # TaskGroup は正常終了時、reader が EOF を読み切るまで待ってくれる
        return proc.returncode or 0

    except asyncio.TimeoutError:
        if proc.returncode is None:
            print('タイムアウトのため終了')
            proc.terminate()
            # proc.kill() ... 強制的に止めるケース
        return proc.returncode if proc.returncode is not None else 1


async def main():
    # 例: “Python自身”を子プロセスとして起動してメッセージを出させる
    code1 = """
import time
from datetime import datetime
for i in range(5):
    print(f'A {i} {datetime.now()}', flush=True)
    time.sleep(0.5)
# エラー出力が発生するはず
raise Exception("Error A")
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

    # 並行に2つの子プロセスを実行（それぞれ10秒タイムアウト）
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(run_and_stream(name, cmd, timeout=1.0)) for name, cmd in cmds]
    for item, task in zip(cmds, tasks):
        print(item[0], task.result())


if __name__ == "__main__":
    install_profile_hooks()
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
    uninstall_profile_hooks()
