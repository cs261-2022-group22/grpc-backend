from compiled_protos.matching_package import GetMatchingMentorReply
from utils.connection_pool import ConnectionPool

matchingServiceConnectionPool = ConnectionPool()


def getMatchingMentorImpl(menteeId: int) -> GetMatchingMentorReply:
    return GetMatchingMentorReply()
