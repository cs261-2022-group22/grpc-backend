from datetime import datetime
from logging import error

import bcrypt
import psycopg
from compiled_protos.account_package import (AuthenticateReply, BusinessArea,
                                             ListBusinessAreasReply,
                                             ProfilesReply, RegistrationReply)
from utils.connection_pool import ConnectionPool

accountServiceConnectionPool = ConnectionPool()

def tryLoginImpl(username: str, password: str) -> AuthenticateReply:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

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
    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def registerUserImpl(name: str, date_of_birth: datetime, email: str, password: str, business_area_id: int):
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    response = RegistrationReply()
    response.status = False  # failure biased

    if (len(password) < 6) or (date_of_birth.date() > datetime.now().date()) or (business_area_id <= 0) or (len(name) == 0) or (len(email) == 0):
        response.status = False
        response.account_id = None
    else:
        try:
            passwordHash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            cur.execute("""INSERT INTO public.account (accountid, name, email, passwordhash, dob, businesssectorid)
                           VALUES (DEFAULT, %s::varchar, %s::varchar, %s::bytea, %s::date, %s::integer) RETURNING accountid;""",
                        (name, email, passwordHash, date_of_birth, business_area_id))

            accountId = cur.fetchone()[0]
            print(f'CreateUser: {cur.rowcount} row affected, inserted rowid {accountId}')
            response.status = True
            response.account_id = accountId
            conn.commit()
        except psycopg.DatabaseError as e:
            error(f'CreateUser: {e}')
            response.status = False
            response.account_id = None
            conn.rollback();

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def accountProfilesImpl(userid: int) -> ProfilesReply:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

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

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def listBusinessAreasImpl() -> ListBusinessAreasReply:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    response = ListBusinessAreasReply()
    cur.execute("SELECT * FROM businesssector;")
    results = cur.fetchall()

    for result in results:
        response.business_areas.append(BusinessArea(result[0], result[1]))

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response
