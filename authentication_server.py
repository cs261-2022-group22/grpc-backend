from concurrent import futures
import logging
import time
from threading import Lock
from queue import Queue

import grpc
import authentication_pb2
import authentication_pb2_grpc

import psycopg2
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

mutex = Lock() #to prevent race conditions

connCurList = [] #does not get manipulated - another version of the collection below
connCurQueue = Queue(maxsize=10) #connections to database and corresponding cursors

class Authenticate(authentication_pb2_grpc.AuthenticateServicer):
    def TryLogin(self, request, context):
        mutex.acquire()
        (conn, cur) = connCurQueue.get_nowait() #cursor for performing sql statements
        mutex.release()

        response = authentication_pb2.AuthenticateReply()
        response.status = False #failure biased

        
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


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    authentication_pb2_grpc.add_AuthenticateServicer_to_server(Authenticate(), server)
    print("Server started. Listening on port 50051.")
    server.add_insecure_port('[::]:50051')

    #create a connection and corresponding cursor for each thread
    for i in range(10):
        conn = psycopg2.connect( #connection to database
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
    #clean up
    for i in range(10):
        (conn, cur) = connCurList[i]
        cur.close()
        conn.close()


if __name__ == '__main__':
    logging.basicConfig()
    serve()