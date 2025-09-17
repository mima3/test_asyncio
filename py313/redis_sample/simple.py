import asyncio
import redis.asyncio as redis
from thread.watch_thread import install_profile_hooks, uninstall_profile_hooks


async def main():
    async with redis.Redis(host="localhost", port=6379, db=0) as client:
        pong = await client.ping()
        print("PING ->", pong)
        res = await client.set("demo:key", "hello")
        print("SET ->", res)
        res = await client.get("demo:key")
        print("GET ->", res)


if __name__ == "__main__":
    install_profile_hooks()
    with asyncio.Runner(debug=True) as runner:
        runner.run(main())
    uninstall_profile_hooks()
