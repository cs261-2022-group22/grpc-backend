from cProfile import run

from compiled_protos.feedback_package import (AddFeedbackReply,
                                              FeedbackServiceBase)
from grpclib.server import Server
from utils.thread_execute import run_in_thread, shutdown_thread_pool

from services.FeedbackServiceImpl import (addDevFeedbackImpl,
                                          addRatingFeedbackImpl,
                                          feedbackServiceConnectionPool)


class FeedbackService(FeedbackServiceBase):
    async def add_feedback_on_mentor(self, mentor_user_id: int, mentee_user_id: int, rating: float) -> AddFeedbackReply:
        return await run_in_thread(addRatingFeedbackImpl, "Mentor", mentor_user_id, mentee_user_id, rating)

    async def add_feedback_on_mentee(self, mentor_user_id: int, mentee_user_id: int, rating: float) -> AddFeedbackReply:
        return await run_in_thread(addRatingFeedbackImpl, "Mentee", mentor_user_id, mentee_user_id, rating)

    async def add_dev_feedback(self, content: str) -> AddFeedbackReply:
        return await run_in_thread(addDevFeedbackImpl, content)


async def beginServe(connectionString: str, port: int, listenAddress: str):
    feedbackServiceConnectionPool.initialise_connection_pool(connectionString)

    global gRPCServer
    gRPCServer = Server([FeedbackService()])
    await gRPCServer.start(listenAddress, port)
    print(f"Feedback Service Server started. Listening on {listenAddress}:{port}")
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
