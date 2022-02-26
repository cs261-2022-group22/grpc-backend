import os
from datetime import datetime
from queue import Queue
from threading import Lock

import bcrypt
import protos.account_package as Account
import psycopg2
from grpclib.server import Server

from utils.thread_execute import run_in_thread

gRPCServer: Server

connMutex = Lock()  # to prevent race conditions
connCurList = []  # does not get manipulated - another version of the collection below
connCurQueue: Queue = Queue(maxsize=10)  # connections to database and corresponding cursors


class AccountService(Account.AccountServiceBase):
    async def try_login(self, username: str, password: str) -> Account.AuthenticateReply:
        return await run_in_thread(tryLogin, username, password)

    async def register_user(self, name: str, date_of_birth: datetime, email: str, password: str, business_area_id: int) -> Account.RegistrationReply:
        return await run_in_thread(registerUser, name, date_of_birth, email, password, business_area_id)

    async def account_profiles(self, userid: int) -> Account.ProfilesReply:
        return await run_in_thread(accountProfiles, userid)


def tryLogin(username: str, password: str) -> Account.AuthenticateReply:
    connMutex.acquire()
    (conn, cur) = connCurQueue.get_nowait()  # cursor for performing sql statements
    connMutex.release()

    response = Account.AuthenticateReply()
    response.status = False  # failure biased

    ###
    cur.execute("SELECT passwordHash, accountId FROM Account WHERE email=%s;", (username,))
    if (resultRow := cur.fetchone()) is not None:
        # The default output format of bytes in the database is memory view. Thus, this
        # must be converted to the bytes datatype for use with brcrypt functions.
        storedPasswordHashBytes = (resultRow[0]).tobytes()
        givenPasswordPlainBytes = password.encode("utf-8")
        if bcrypt.checkpw(givenPasswordPlainBytes, storedPasswordHashBytes):
            response.id = resultRow[1]
            response.status = True
    ###

    conn.commit()

    connMutex.acquire()
    connCurQueue.put_nowait((conn, cur))
    connMutex.release()

    return response


def registerUser(name: str, date_of_birth: datetime, email: str, password: str, business_area_id: int):
    connMutex.acquire()
    (conn, cur) = connCurQueue.get_nowait()  # cursor for performing sql statements
    connMutex.release()

    response = Account.RegistrationReply()
    response.status = False  # failure biased

    ###
    # print(request.name)
    # print(request.email)
    # print(request.password)
    # print(request.businessarea.id)
    # print(request.businessarea.name)
    print(date_of_birth)

    ###

    conn.commit()

    connMutex.acquire()
    connCurQueue.put_nowait((conn, cur))
    connMutex.release()


def accountProfiles(userid: int) -> Account.ProfilesReply:
    connMutex.acquire()
    (conn, cur) = connCurQueue.get_nowait()  # cursor for performing sql statements
    connMutex.release()

    response = Account.ProfilesReply()
    response.is_mentor = False  # failure biased
    response.is_mentee = False

    ###
    cur.execute("SELECT mentorId FROM Mentor WHERE accountId=%s;",
                (userid,))
    if cur.fetchone() is not None:
        response.is_mentor = True

    cur.execute("SELECT menteeId FROM Mentee WHERE accountId=%s;",
                (userid,))
    if cur.fetchone() is not None:
        response.is_mentee = True
    ###

    conn.commit()

    connMutex.acquire()
    connCurQueue.put_nowait((conn, cur))
    connMutex.release()

    return response


async def serve(port: int):
    # create a connection and corresponding cursor for each thread
    for _ in range(10):
        # connection to database
        conn: psycopg2.connection = psycopg2.connect(
            "dbname=" +
            os.getenv("POSTGRES_DATABASE", "mentoring") +
            " user=" +
            os.getenv("POSTGRES_USER", "") +
            " password=" +
            os.getenv("POSTGRES_PASSWORD", "") +
            " host=" +
            os.getenv("POSTGRES_HOST", "localhost") +
            " port=" +
            os.getenv("POSTGRES_PORT", "")
        )
        cur: psycopg2.cursor = conn.cursor()
        connCurQueue.put_nowait((conn, cur))
        connCurList.append((conn, cur))

    global gRPCServer
    gRPCServer = Server([AccountService()])
    await gRPCServer.start("127.0.0.1", port)
    print("Server started. Listening on port:", port)
    await gRPCServer.wait_closed()


def close():
    if gRPCServer.is_serving:
        gRPCServer.close()

    # clean up
    for i in range(10):
        (conn, cur) = connCurList[i]
        cur.close()
        conn.close()
    print("Server stopped.")
    pass
