import asyncio
from pathlib import Path
import mimetypes
from typing import Iterable, Optional, Any, AsyncContextManager, cast
import aioboto3
from botocore.config import Config
from boto3.s3.transfer import TransferConfig
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


async def upload_files_to_s3(
    files: Iterable[Path | str],
    bucket: str,
    *,
    prefix: str = "",
    region: Optional[str] = None,
    multipart_threshold_mb: int = 8,  # これ以上のサイズでマルチパート化
    extra_args: Optional[dict] = None,  # ACL/ServerSideEncryptionなどを入れる
    endpoint_url: Optional[str] = None,
    use_path_style: Optional[bool] = None,  # Noneならendpoint指定時は自動でTrue
) -> list[dict]:
    """
    指定ファイル群を S3 の bucket/prefix 配下に非同期でアップロードする。

    returns: [{'file': '...','key':'...','status':'uploaded|skipped'}...]
    """

    file_list = [Path(p).resolve() for p in files]

    # S3 転送設定（マルチパート・同時パート数など）
    transfer_config = TransferConfig(
        multipart_threshold=multipart_threshold_mb * 1024 * 1024,
        multipart_chunksize=8 * 1024 * 1024,
        # max_concurrency=1,
    )

    b_cfg = Config(
        region_name=region,
        retries={"max_attempts": 10, "mode": "adaptive"},
        # max_pool_connections=2,
    )
    if use_path_style is None:
        use_path_style = bool(endpoint_url)
    verify_ssl = not (endpoint_url and endpoint_url.startswith("http://"))
    use_ssl = True
    if endpoint_url:
        use_ssl = endpoint_url.startswith("https://")

    session = aioboto3.Session()

    results: list[dict] = []
    s3_cm: AsyncContextManager[Any] = cast(
        AsyncContextManager[Any],
        session.client(
            "s3",
            endpoint_url=endpoint_url,
            config=b_cfg,
            use_ssl=use_ssl,
            verify=verify_ssl,
        ),
    )
    async with s3_cm as s3:
        async def put_one(path: Path):
            # S3 の Key を決める（prefix + ファイル名）
            rel = path.name
            key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel

            # Content-Type を推定
            ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
            ea = {"ContentType": ctype}
            if extra_args:
                ea.update(extra_args)
            # 高水準API: マルチパートを自動処理
            await s3.upload_file(
                Filename=str(path),
                Bucket=bucket,
                Key=key,
                ExtraArgs=ea,
                Config=transfer_config,
            )
            results.append({"file": str(path), "key": key, "status": "uploaded"})

        await asyncio.gather(*(put_one(p) for p in file_list))

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
        region="ap-northeast-1",
        extra_args={  # 任意（例：公開アクセスは慎重に）
            # "ACL": "private",
            # "ServerSideEncryption": "AES256",
        },
        endpoint_url="http://localhost:4566/",
    )
    for r in out:
        print(r)


if __name__ == "__main__":
    install_profile_hooks()
    asyncio.run(main())
    uninstall_profile_hooks()
