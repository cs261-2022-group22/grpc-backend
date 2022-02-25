import asyncio
import logging
import os

import Services.AccountService as AccountService
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig()

    port = int(os.getenv("GRPC_BACKEND_PORT") or 50051)
    if port < 1 or port > 65535:
        print("Invalid port number:", port)
        exit()

    async def main():
        await AccountService.serve(port)

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main())
        loop.close()
    except KeyboardInterrupt:
        AccountService.close()
