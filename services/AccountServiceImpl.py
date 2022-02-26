from datetime import datetime
from queue import Queue
from threading import Lock

import bcrypt
import psycopg
from compiled_protos.account_package import (AuthenticateReply, ProfilesReply,
                                             RegistrationReply)

connMutex = Lock()  # to prevent race conditions
connCurList: list[tuple[psycopg.Connection, psycopg.Cursor]] = []  # does not get manipulated - another version of the collection below
connCurQueue: Queue[tuple[psycopg.Connection, psycopg.Cursor]] = Queue(maxsize=16)  # connections to database and corresponding cursors


def tryLoginImpl(username: str, password: str) -> AuthenticateReply:
    connMutex.acquire()
    (conn, cur) = connCurQueue.get_nowait()  # cursor for performing sql statements
    connMutex.release()

    response = AuthenticateReply()
    response.status = False  # failure biased

    ###
    cur.execute("SELECT passwordHash, accountId FROM Account WHERE email=%s;", (username,))
    if (resultRow := cur.fetchone()) is not None:
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

    response = RegistrationReply()
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
    return response


def accountProfilesImpl(userid: int) -> ProfilesReply:
    connMutex.acquire()
    (conn, cur) = connCurQueue.get_nowait()  # cursor for performing sql statements
    connMutex.release()

    response = ProfilesReply()
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
