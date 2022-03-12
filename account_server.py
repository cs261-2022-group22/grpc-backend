import asyncio

import services.AccountService as AccountService
from utils import InitService

if __name__ == '__main__':
    port, ConnectionString, listenAddress = InitService("ACCOUNT")
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(AccountService.beginServe(ConnectionString, port, listenAddress))
    except KeyboardInterrupt:
        loop.run_until_complete(AccountService.endServe())
    finally:
        loop.close()
