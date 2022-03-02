import sys
sys.path.append("..")

import asyncio
from grpclib.client import Channel
from compiled_protos.account_package import AccountServiceStub

async def main():
    channel = Channel(host="127.0.0.1", port=50051)
    service = AccountServiceStub(channel)
    response = await service.try_login(username="test@gmail.com", password="test")
    print(response)

    channel.close()

asyncio.run(main())  # python 3.7+