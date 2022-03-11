""" Implements a connection queue. Each element should be a tuple of a 
connection and a corresponding cursor. A list, that should remain static, is 
provided to keep track of every connection, and corresponding cursor, regardless 
of the state of the queue. """

import inspect
from queue import Queue
from threading import Lock

import psycopg


class ConnectionPool:
    def __init__(self) -> None:
        self.connMutex = Lock()  # to prevent race conditions
        self.connCurList: list[tuple[psycopg.Connection, psycopg.Cursor]] = []  # does not get manipulated - another version of the collection below
        self.connCurQueue: Queue[tuple[psycopg.Connection, psycopg.Cursor]] = Queue(maxsize=16)  # connections to database and corresponding cursors

    def acquire_from_connection_pool(self) -> tuple[psycopg.Connection, psycopg.Cursor]:
        funcName = inspect.currentframe().f_back.f_code.co_name
        print(f'Processing "{funcName}"')
        self.connMutex.acquire()
        # cursor for performing sql statements
        (conn, cur) = self.connCurQueue.get_nowait()
        self.connMutex.release()
        return (conn, cur)

    def release_to_connection_pool(self, conn: psycopg.Connection, cur: psycopg.Cursor) -> None:
        conn.commit()
        self.connMutex.acquire()
        self.connCurQueue.put_nowait((conn, cur))
        self.connMutex.release()

    def initialise_connection_pool(self, connectionString: str) -> None:
        # create a connection and corresponding cursor for each thread
        for _ in range(16):
            # connect to database
            conn: psycopg.Connection = psycopg.connect(connectionString)
            cur: psycopg.Cursor = conn.cursor()
            self.connCurQueue.put_nowait((conn, cur))
            self.connCurList.append((conn, cur))

    def shutdown_connection_pool(self) -> None:
        for i in range(16):
            (conn, cur) = self.connCurList[i]
            cur.close()
            conn.close()
