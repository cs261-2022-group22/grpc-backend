from compiled_protos.matching_package import (GetMenteesReply,
                                              MatchingServiceBase,
                                              MenteeToMentorMatchingReply)
from grpclib.server import Server
from utils.thread_execute import run_in_thread, shutdown_thread_pool

from services.MatchingServiceImpl import (getMatchingMentorImpl,
                                          getMenteesByMentorIdImpl,
                                          matchingServiceConnectionPool,
                                          tryMatchImpl)


class MatchingService(MatchingServiceBase):
    async def try_match(self, mentee_user_id: int) -> MenteeToMentorMatchingReply:
        return await run_in_thread(tryMatchImpl, mentee_user_id)

    async def get_matching_mentor(self, mentee_user_id: int) -> MenteeToMentorMatchingReply:
        return await run_in_thread(getMatchingMentorImpl, mentee_user_id)

    async def get_mentees_by_mentor_id(self, mentor_user_id: int) -> GetMenteesReply:
        return await run_in_thread(getMenteesByMentorIdImpl, mentor_user_id)


async def beginServe(connectionString: str, port: int, listenAddress: str):
    matchingServiceConnectionPool.initialise_connection_pool(connectionString)

    global gRPCServer
    gRPCServer = Server([MatchingService()])
    await gRPCServer.start(listenAddress, port)
    print(f"Matching Service Server started. Listening on {listenAddress}:{port}")
    await gRPCServer.wait_closed()


async def endServe():
    print("Stopping Matching Service...")
    shutdown_thread_pool()

    # clean up connection pool
    matchingServiceConnectionPool.shutdown_connection_pool()

    global gRPCServer
    gRPCServer.close()
    await gRPCServer.wait_closed()
    print("Matching Service Stopped.")
