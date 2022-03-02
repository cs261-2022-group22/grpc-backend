import asyncio
from grpclib.client import Channel
import compiled_protos.account_package as AccountPackage

async def main():
    channel = Channel(host="127.0.0.1", port=50051)
    service = AccountPackage.AccountServiceStub(channel)
    response = await service.try_login(username="test@gmail.com", password="est")
    print(response)

    channel.close()

asyncio.run(main())  # python 3.7 only