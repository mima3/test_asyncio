import asyncio
import threading
import aiofiles
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


async def read_file(input_path: str) -> list[str]:
    lines = []
    async with aiofiles.open(input_path, mode="r") as f:
        async for line in f:
            lines.append(line)
    return lines


async def main():
    print(f"start thread_id:{threading.get_ident()}")
    file_path_list = [
        "../docker/ssh/downloads/0001.md",
        "../docker/ssh/downloads/0002.md",
        "../docker/ssh/downloads/0003.md",
        "../docker/ssh/downloads/0004.md",
        "../docker/ssh/downloads/0005.md",
        "../docker/ssh/downloads/0006.md",
        "../docker/ssh/downloads/0007.md",
        "../docker/ssh/downloads/0008.md",
        "../docker/ssh/downloads/0009.md",
        "../docker/ssh/downloads/0010.md",
        "../docker/ssh/downloads/0011.md",
        "../docker/ssh/downloads/0012.md",
        "../docker/ssh/downloads/0013.md",
        "../docker/ssh/downloads/0014.md",
        "../docker/ssh/downloads/0015.md",
        "../docker/ssh/downloads/0016.md",
        "../docker/ssh/downloads/0017.md",
        "../docker/ssh/downloads/0018.md",
        "../docker/ssh/downloads/0019.md",
        "../docker/ssh/downloads/0020.md",
    ]
    result = []
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for file_path in file_path_list:
            tasks.append(tg.create_task(read_file(file_path)))
    for task in tasks:
        result.append(task.result())
    for item in result:
        print(item[0])
    print("result...", len(result))


if __name__ == "__main__":
    install_profile_hooks()
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
    uninstall_profile_hooks()
