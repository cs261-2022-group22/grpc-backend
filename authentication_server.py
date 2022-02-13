from concurrent import futures
import logging

import grpc
import authentication_pb2
import authentication_pb2_grpc

import psycopg2
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class Authenticate(authentication_pb2_grpc.AuthenticateServicer):
    def TryLogin(self, request, context):
        response = authentication_pb2.AuthenticateReply()
        response.status = "FAILURE" #failure biased

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
        cur = conn.cursor() #cursor for performing sql statements
        
        ###
        cur.execute("SELECT passwordHash, accountId FROM Account WHERE email=%s;", (request.username,))
        if (resultRow := cur.fetchone()) is not None:
            # The default output format of bytes in the database is memory view. Thus, this 
            # must be converted to the bytes datatype for use with brcrypt functions.
            storedPasswordHashBytes = (resultRow[0]).tobytes()
            givenPasswordPlainBytes = request.password.encode("utf-8")
            if bcrypt.checkpw(givenPasswordPlainBytes, storedPasswordHashBytes):
                response.id = resultRow[1]
                response.status = "SUCCESS"
        ###

        conn.commit()

        cur.close()
        conn.close()

        return response

        # if request.username == "test@gmail.com" and request.password == "test":
        #     response.id = 1
        #     response.status = "SUCCESS"
        # else:
        #     response.status = "FAILURE" 

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    authentication_pb2_grpc.add_AuthenticateServicer_to_server(Authenticate(), server)
    print("Server started. Listening on port 50051.")
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()