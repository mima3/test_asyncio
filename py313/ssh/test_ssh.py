import asyncio
import os
import posixpath
import asyncssh
from datetime import datetime
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks

HOST = "127.0.0.1"
PORT = 2222
USERNAME = "test_user"
PASSWORD = "pass"
CONCURRENCY = 5


download_list = [
    ("/home/test_user/downloads/0001.md", "./tmp/0001.md"),
    ("/home/test_user/downloads/0002.md", "./tmp/0002.md"),
    ("/home/test_user/downloads/0003.md", "./tmp/0003.md"),
    ("/home/test_user/downloads/0004.md", "./tmp/0004.md"),
    ("/home/test_user/downloads/0005.md", "./tmp/0005.md"),
    ("/home/test_user/downloads/0006.md", "./tmp/0006.md"),
    ("/home/test_user/downloads/0007.md", "./tmp/0007.md"),
    ("/home/test_user/downloads/0008.md", "./tmp/0008.md"),
    ("/home/test_user/downloads/0009.md", "./tmp/0009.md"),
    ("/home/test_user/downloads/0010.md", "./tmp/0010.md"),
    ("/home/test_user/downloads/0011.md", "./tmp/0011.md"),
    ("/home/test_user/downloads/0012.md", "./tmp/0012.md"),
    ("/home/test_user/downloads/0013.md", "./tmp/0013.md"),
    ("/home/test_user/downloads/0014.md", "./tmp/0014.md"),
    ("/home/test_user/downloads/0015.md", "./tmp/0015.md"),
    ("/home/test_user/downloads/0016.md", "./tmp/0016.md"),
    ("/home/test_user/downloads/0017.md", "./tmp/0017.md"),
    ("/home/test_user/downloads/0018.md", "./tmp/0018.md"),
    ("/home/test_user/downloads/0019.md", "./tmp/0019.md"),
    ("/home/test_user/downloads/0020.md", "./tmp/0020.md"),
    ("/home/test_user/downloads/0021.md", "./tmp/0021.md"),
    ("/home/test_user/downloads/0022.md", "./tmp/0022.md"),
    ("/home/test_user/downloads/0023.md", "./tmp/0023.md"),
    ("/home/test_user/downloads/0024.md", "./tmp/0024.md"),
    ("/home/test_user/downloads/0025.md", "./tmp/0025.md"),
    ("/home/test_user/downloads/0026.md", "./tmp/0026.md"),
    ("/home/test_user/downloads/0027.md", "./tmp/0027.md"),
    ("/home/test_user/downloads/0028.md", "./tmp/0028.md"),
    ("/home/test_user/downloads/0029.md", "./tmp/0029.md"),
    ("/home/test_user/downloads/0030.md", "./tmp/0030.md"),
]


async def sftp_get(sftp: asyncssh.SFTPClient, remote: str, local: str, sem: asyncio.Semaphore) -> str:
    async with sem:
        # ダウンロード先のローカルにフォルダを作る
        os.makedirs(os.path.dirname(local) or ".", exist_ok=True)

        try:
            # ダウンロード
            await sftp.get(remote, local)
            print(f"[GET ] {remote} -> {local}")
            return local
        except (asyncssh.Error, OSError) as e:
            print(e)
            return ""


async def sftp_put(sftp: asyncssh.SFTPClient, local: str, remote: str, sem: asyncio.Semaphore):
    async with sem:
        # リモートパスは POSIX（/ 区切り）
        parent_dir = posixpath.dirname(remote) or "."
        try:
            await sftp.stat(parent_dir)
        except Exception:
            # 無ければ掘る（既にあるときは失敗する可能性があるので try/except）
            try:
                await sftp.mkdir(parent_dir)
            except Exception:
                pass

        await sftp.put(local, remote)
        print(f"[PUT ] {local} -> {remote}")


async def main() -> None:
    sem = asyncio.Semaphore(CONCURRENCY)
    # パスワード認証。known_hosts=None は“ホスト鍵を検証しない”（テスト専用）
    async with asyncssh.connect(
        HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        client_keys=[],
        known_hosts=None,
    ) as conn:
        async with conn.start_sftp_client() as sftp:
            download_tasks = []
            async with asyncio.TaskGroup() as tg:
                for remote_path, local_path in download_list:
                    download_tasks.append(tg.create_task(sftp_get(sftp, remote_path, local_path, sem)))
            # 失敗も回収してログに出す
            upload_tasks = []
            downloads = [task.result() for task in download_tasks]
            async with asyncio.TaskGroup() as tg:
                for i, item in enumerate(downloads):
                    if not item:
                        print(f"[ERR ] task#{i}: {item!r}")
                    else:
                        local_path: str = item
                        with open(item, "a") as f:
                            print(f"{datetime.now()} appended", file=f)
                        upload_tasks.append(
                            tg.create_task(sftp_put(sftp, item, f"/home/test_user/uploads/upload_{i + 1:04d}.md", sem))
                        )
            uploads = [task.result() for task in upload_tasks]
            for i, item in enumerate(uploads):
                if isinstance(item, Exception):
                    print(f"[ERR ] task#{i}: {item!r}")
                else:
                    print(f"[OK  ] task#{i}:")


if __name__ == "__main__":
    install_profile_hooks()
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
    uninstall_profile_hooks()
