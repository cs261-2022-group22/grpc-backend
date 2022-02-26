import os
from datetime import datetime
from queue import Queue
from threading import Lock
from typing import List, Tuple

import bcrypt
import protos.account_package as Account
import psycopg
from grpclib.server import Server

from utils.thread_execute import run_in_thread

gRPCServer: Server

connMutex = Lock()  # to prevent race conditions
connCurList: List[Tuple[psycopg.Connection, psycopg.Cursor]] = []  # does not get manipulated - another version of the collection below
connCurQueue: Queue[Tuple[psycopg.Connection, psycopg.Cursor]] = Queue(maxsize=10)  # connections to database and corresponding cursors


def tryLoginImpl(username: str, password: str) -> Account.AuthenticateReply:
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
        storedPasswordHashBytes = resultRow[0]
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


def registerUserImpl(name: str, date_of_birth: datetime, email: str, password: str, business_area_id: int):
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


def accountProfilesImpl(userid: int) -> Account.ProfilesReply:
    connMutex.acquire()
    (conn, cur) = connCurQueue.get_nowait()  # cursor for performing sql statements
    connMutex.release()

    response = Account.ProfilesReply()
    response.is_mentor = False  # failure biased
    response.is_mentee = False

    ###
    cur.execute("SELECT mentorId FROM Mentor WHERE accountId=%s;", (userid,))
    if cur.fetchone() is not None:
        response.is_mentor = True

    cur.execute("SELECT menteeId FROM Mentee WHERE accountId=%s;", (userid,))
    if cur.fetchone() is not None:
        response.is_mentee = True
    ###

    conn.commit()

    connMutex.acquire()
    connCurQueue.put_nowait((conn, cur))
    connMutex.release()

    return response
