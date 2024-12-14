import os
import asyncio
from alist import AList, AListUser

alist_user = None
alist_client = None


async def init_alist():
    global alist_user, alist_client
    if os.getenv("ALIST_SERVER"):
        alist_user = AListUser(os.getenv("ALIST_USERNAME"), os.getenv("ALIST_PASSWORD"))
        alist_client = AList(os.getenv("ALIST_SERVER"))  # 服务器 URL
        await alist_client.login(alist_user)  # 异步调用


asyncio.run(init_alist())
