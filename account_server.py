import asyncio
import logging
import os

from dotenv import load_dotenv

import services.AccountService as AccountService

# The entry-point code of Account Service

if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig()

    port = int(os.getenv("GRPC_BACKEND_PORT") or 50051)
    if port < 1 or port > 65535:
        print("Invalid port number:", port)
        exit()

    DBName = os.getenv("POSTGRES_DATABASE", "mentoring")
    DBUser = os.getenv("POSTGRES_USER", "")
    DBPassword = os.getenv("POSTGRES_PASSWORD", "")
    DBHost = os.getenv("POSTGRES_HOST", "localhost")
    DBPort = os.getenv("POSTGRES_PORT", "")

    ConnectionString = f'dbname={DBName} user={DBUser} password={DBPassword} host={DBHost} port={DBPort}'

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(AccountService.beginServe(ConnectionString, port))
    except KeyboardInterrupt:
        loop.run_until_complete(AccountService.endServe())
    finally:
        loop.close()
