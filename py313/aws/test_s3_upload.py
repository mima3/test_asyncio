import asyncio
import os
from pathlib import Path
from typing import Iterable
import aioboto3
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


# localstackを使用する場合はENDPOINTを設定する
os.environ["AWS_ENDPOINT_URL_S3"] = "http://localhost:4566/"


async def upload_files_to_s3(
    files: Iterable[Path | str], bucket: str, *, prefix: str = "", max_concurrency_file: int = 5
) -> list[dict]:
    """
    指定ファイル群を S3 の bucket/prefix 配下に非同期でアップロードする。

    returns: [{'file': '...','key':'...','status':'uploaded|skipped'}...]
    """
    file_list = [Path(p).resolve() for p in files]
    session = aioboto3.Session()
    results: list[dict] = []
    sem = asyncio.Semaphore(max_concurrency_file)

    async with session.client("s3") as s3:

        async def put_one(path: Path):
            print("  start put_one", path)
            async with sem:
                print("  start put_one after sem", path)
                # S3 の Key を決める（prefix + ファイル名）
                rel = path.name
                key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
                # 高水準API: マルチパートを自動処理
                await s3.upload_file(
                    Filename=str(path),
                    Bucket=bucket,
                    Key=key,
                )
                results.append({"file": str(path), "key": key, "status": "uploaded"})
            print("  end put_one", path)

        async with asyncio.TaskGroup() as tg:
            for p in file_list:
                tg.create_task(put_one(p))

    return results


download_list = [
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
    "../docker/ssh/downloads/0021.md",
    "../docker/ssh/downloads/0022.md",
    "../docker/ssh/downloads/0023.md",
    "../docker/ssh/downloads/0024.md",
    "../docker/ssh/downloads/0025.md",
    "../docker/ssh/downloads/0026.md",
    "../docker/ssh/downloads/0027.md",
    "../docker/ssh/downloads/0028.md",
    "../docker/ssh/downloads/0029.md",
    "../docker/ssh/downloads/0030.md",
]


async def main() -> None:
    out = await upload_files_to_s3(
        download_list,
        bucket="my-bucket",
        prefix="income",
    )
    for r in out:
        print(r)


if __name__ == "__main__":
    install_profile_hooks()
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
    uninstall_profile_hooks()
