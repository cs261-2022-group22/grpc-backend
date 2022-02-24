import logging
import os
import time
from concurrent import futures
from queue import Queue
from threading import Lock

import bcrypt
import grpc
import psycopg2
from dotenv import load_dotenv

import protos.account_pb2
import protos.account_pb2_grpc

load_dotenv()

mutex = Lock()  # to prevent race conditions
connCurList = []  # does not get manipulated - another version of the collection below
connCurQueue = Queue(maxsize=10)  # connections to database and corresponding cursors


class AccountServiceHandler(protos.account_pb2_grpc.AccountServiceServicer):
    def TryLogin(self, request, context):
        mutex.acquire()
        (conn, cur) = connCurQueue.get_nowait()  # cursor for performing sql statements
        mutex.release()

        response = protos.account_pb2.AuthenticateReply()
        response.status = False  # failure biased

        ###
        cur.execute("SELECT passwordHash, accountId FROM Account WHERE email=%s;", (request.username,))
        if (resultRow := cur.fetchone()) is not None:
            # The default output format of bytes in the database is memory view. Thus, this
            # must be converted to the bytes datatype for use with brcrypt functions.
            storedPasswordHashBytes = (resultRow[0]).tobytes()
            givenPasswordPlainBytes = request.password.encode("utf-8")
            if bcrypt.checkpw(givenPasswordPlainBytes, storedPasswordHashBytes):
                response.id = resultRow[1]
                response.status = True
        ###

        conn.commit()

        mutex.acquire()
        connCurQueue.put_nowait((conn, cur))
        mutex.release()

        return response

    def UserRegistration(self, request, context):
        mutex.acquire()
        (conn, cur) = connCurQueue.get_nowait()  # cursor for performing sql statements
        mutex.release()

        response = protos.account_pb2.RegistrationReply()
        response.status = False  # failure biased

        ###
        # print(request.name)
        # print(request.email)
        # print(request.password)
        # print(request.businessarea.id)
        # print(request.businessarea.name)
        # print(request.dateofbirth.ToDatetime())

        ###

        conn.commit()

        mutex.acquire()
        connCurQueue.put_nowait((conn, cur))
        mutex.release()

        return response

    def AccountProfiles(self, request, context):
        mutex.acquire()
        (conn, cur) = connCurQueue.get_nowait()  # cursor for performing sql statements
        mutex.release()

        response = protos.account_pb2.ProfilesReply()
        response.isMentor = False  # failure biased
        response.isMentee = False

        ###
        cur.execute("SELECT mentorId FROM Mentor WHERE accountId=%s;",
                    (request.userid,))
        if cur.fetchone() is not None:
            response.isMentor = True

        cur.execute("SELECT menteeId FROM Mentee WHERE accountId=%s;",
                    (request.userid,))
        if cur.fetchone() is not None:
            response.isMentee = True
        ###

        conn.commit()

        mutex.acquire()
        connCurQueue.put_nowait((conn, cur))
        mutex.release()

        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protos.account_pb2_grpc.add_AccountServiceServicer_to_server(AccountServiceHandler(), server)
    port = int(os.getenv("GRPC_BACKEND_PORT") or 50051)
    if port < 1 or port > 65535:
        print("Invalid port number:", port)
        exit()

    print("Server started. Listening on port:", port)
    server.add_insecure_port('[::]:' + str(port))
    # create a connection and corresponding cursor for each thread
    for i in range(10):
        conn = psycopg2.connect(  # connection to database
            "dbname=" +
            os.getenv("POSTGRES_DATABASE") +
            " user=" +
            os.getenv("POSTGRES_USER") +
            " password=" +
            os.getenv("POSTGRES_PASSWORD") +
            " host=" +
            os.getenv("POSTGRES_HOST") +
            " port=" +
            os.getenv("POSTGRES_PORT")
        )
        cur = conn.cursor()
        connCurQueue.put_nowait((conn, cur))
        connCurList.append((conn, cur))

    server.start()
    try:
        while True:
            time.sleep(100000)
    except KeyboardInterrupt:
        server.stop(10)

    print("Server stopped.")
    # clean up
    for i in range(10):
        (conn, cur) = connCurList[i]
        cur.close()
        conn.close()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
