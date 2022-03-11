from compiled_protos.feedback_package import (FeedbackServiceBase, 
                                            AddFeedbackReply)
from grpclib.server import Server
from utils.thread_execute import run_in_thread, shutdown_thread_pool

from services.FeedbackServiceImpl import (feedbackServiceConnectionPool, 
                                        addFeedbackOnMentorImpl)


class FeedbackService(FeedbackServiceBase):
    async def add_feedback_on_mentor(self, mentor_user_id: int, mentee_user_id: int, rating: float) -> AddFeedbackReply:
        return await run_in_thread(addFeedbackOnMentorImpl, mentor_user_id, mentee_user_id, rating)


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
