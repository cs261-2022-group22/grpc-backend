from compiled_protos.feedback_package import (FeedbackServiceBase)
from grpclib.server import Server
from utils.thread_execute import run_in_thread, shutdown_thread_pool

from services.FeedbackServiceImpl import (feedbackServiceConnectionPool)


class FeedbackService(FeedbackServiceBase):
    pass


async def beginServe(connectionString: str, port: int):
    feedbackServiceConnectionPool.initialise_connection_pool(connectionString)

    global gRPCServer
    gRPCServer = Server([FeedbackService()])
    await gRPCServer.start("127.0.0.1", port)
    print("Feedback Service Server started. Listening on port:", port)
    await gRPCServer.wait_closed()


async def endServe():
    print("Stopping Feedback Service...")
    shutdown_thread_pool()

    # clean up connection pool
    feedbackServiceConnectionPool.shutdown_connection_pool()

    global gRPCServer
    gRPCServer.close()
    await gRPCServer.wait_closed()
    print("Feedback Service Stopped.")
