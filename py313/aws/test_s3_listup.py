import os
import asyncio
import aioboto3
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks

# localstackを使用する場合はENDPOINTを設定する
os.environ["AWS_ENDPOINT_URL_S3"] = "http://localhost:4566/"


async def main():
    session = aioboto3.Session()
    async with session.resource("s3") as s3:
        bucket = await s3.Bucket("my-bucket")
        async for s3_object in bucket.objects.all():
            print(s3_object)


if __name__ == "__main__":
    install_profile_hooks()
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
    uninstall_profile_hooks()
