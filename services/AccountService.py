
import psycopg
from grpclib.server import Server
from protos.account_package import *
from utils.thread_execute import run_in_thread

from Services.AccountServiceImpl import (accountProfilesImpl, connCurList,
                                         connCurQueue, registerUserImpl,
                                         tryLoginImpl)

gRPCServer: Server


class AccountService(AccountServiceBase):
    async def try_login(self, username: str, password: str) -> AuthenticateReply:
        return await run_in_thread(tryLoginImpl, username, password)

    async def register_user(self, name: str, date_of_birth: datetime, email: str, password: str, business_area_id: int) -> RegistrationReply:
        return await run_in_thread(registerUserImpl, name, date_of_birth, email, password, business_area_id)

    async def account_profiles(self, userid: int) -> ProfilesReply:
        return await run_in_thread(accountProfilesImpl, userid)


async def beginServe(connectionString: str, port: int):
    # create a connection and corresponding cursor for each thread
    for _ in range(16):
        # connect to database
        conn: psycopg.Connection = psycopg.connect(connectionString)
        cur: psycopg.Cursor = conn.cursor()
        connCurQueue.put_nowait((conn, cur))
        connCurList.append((conn, cur))

    global gRPCServer
    gRPCServer = Server([AccountService()])
    await gRPCServer.start("127.0.0.1", port)
    print("Account Service Server started. Listening on port:", port)
    await gRPCServer.wait_closed()


def stopServe():
    global gRPCServer
    if gRPCServer.is_serving:
        gRPCServer.close()

    # clean up
    for i in range(16):
        (conn, cur) = connCurList[i]
        cur.close()
        conn.close()
    print("Account Service Server stopped.")
