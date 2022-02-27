""" Implements a connection queue. Each element should be a tuple of a 
connection and a corresponding cursor. A list, that should remain static, is 
provided to keep track of every connection, and corresponding cursor, regardless 
of the state of the queue. """

import inspect
from queue import Queue
from threading import Lock

import psycopg

connMutex = Lock()  # to prevent race conditions
connCurList: list[tuple[psycopg.Connection, psycopg.Cursor]] = []  # does not get manipulated - another version of the collection below
connCurQueue: Queue[tuple[psycopg.Connection, psycopg.Cursor]] = Queue(maxsize=16)  # connections to database and corresponding cursors


def acquire_from_connection_pool():
    funcName = inspect.currentframe().f_back.f_code.co_name
    print(f'Processing "{funcName}"')
    connMutex.acquire()
    # cursor for performing sql statements
    (conn, cur) = connCurQueue.get_nowait()
    connMutex.release()
    return (conn, cur)


def release_to_connection_pool(conn: psycopg.Connection, cur: psycopg.Cursor):
    connMutex.acquire()
    connCurQueue.put_nowait((conn, cur))
    connMutex.release()


def initialise_connection_pool(connectionString: str):
    # create a connection and corresponding cursor for each thread
    for _ in range(16):
        # connect to database
        conn: psycopg.Connection = psycopg.connect(connectionString)
        cur: psycopg.Cursor = conn.cursor()
        connCurQueue.put_nowait((conn, cur))
        connCurList.append((conn, cur))


def shutdown_connection_pool():
    for i in range(16):
        (conn, cur) = connCurList[i]
        cur.close()
        conn.close()