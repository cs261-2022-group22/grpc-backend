import logging
import os
from dotenv import load_dotenv


def InitService(port_env_name: str):
    load_dotenv()
    logging.basicConfig()

    port = int(os.getenv(port_env_name) or 50051)
    if port < 1 or port > 65535:
        print("Invalid port number:", port)
        exit(1)

    DBName = os.getenv("POSTGRES_DATABASE", "mentoring")
    DBUser = os.getenv("POSTGRES_USER", "")
    DBPassword = os.getenv("POSTGRES_PASSWORD", "")
    DBHost = os.getenv("POSTGRES_HOST", "localhost")
    DBPort = os.getenv("POSTGRES_PORT", "")

    ConnectionString = f'dbname={DBName} user={DBUser} password={DBPassword} host={DBHost} port={DBPort}'
    return port, ConnectionString
