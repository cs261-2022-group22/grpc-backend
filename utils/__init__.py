import logging
import os
from dotenv import load_dotenv

def GetConnectionString():
    load_dotenv()

    DBName = os.getenv("POSTGRES_DATABASE", "mentoring")
    DBUser = os.getenv("POSTGRES_USER", "")
    DBPassword = os.getenv("POSTGRES_PASSWORD", "")
    DBHost = os.getenv("POSTGRES_HOST", "localhost")
    DBPort = os.getenv("POSTGRES_PORT", "")

    return f'dbname={DBName} user={DBUser} password={DBPassword} host={DBHost} port={DBPort}'

def InitService(port_env_name: str):
    load_dotenv()
    logging.basicConfig()

    port = int(os.getenv(port_env_name) or 50051)
    if port < 1 or port > 65535:
        print("Invalid port number:", port)
        exit(1)

    ConnectionString = GetConnectionString()
    return port, ConnectionString
