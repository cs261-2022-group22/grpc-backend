import random
from compiled_protos.matching_package import GetMatchingMentorReply
from utils.connection_pool import ConnectionPool

matchingServiceConnectionPool = ConnectionPool()

MENTEE_INFO_QUERY_STRING = """
SELECT dob, accountid, businesssectorid
FROM mentee
    NATURAL JOIN account
    NATURAL LEFT JOIN businesssector
WHERE menteeid = %s;
"""

# TODO: Better matching, based on DoB, feedback metrics, skills
SELECT_MENTOR_BASED_ON_MATCHING_BUSINESS_SECTOR = """
SELECT mentorid, name FROM mentor
    NATURAL LEFT JOIN account
    NATURAL LEFT JOIN businesssector
WHERE businesssectorid = %s;
"""


def getMatchingMentorImpl(menteeId: int) -> GetMatchingMentorReply:
    menteeId = 1
    (conn, cur) = matchingServiceConnectionPool.acquire_from_connection_pool()

    # Step 1: Figure out the businessArea of current mentee
    cur.execute(MENTEE_INFO_QUERY_STRING, (menteeId,))
    (_, _, bussinessAreaId) = cur.fetchone()

    # Step 2: RANDOMLY choose a mentor on this
    cur.execute(SELECT_MENTOR_BASED_ON_MATCHING_BUSINESS_SECTOR, (bussinessAreaId,))
    mentors = cur.fetchall()
    (mentor_id, mentor_name) = random.choice(mentors)

    response = GetMatchingMentorReply()
    response.mentor_id = mentor_id
    response.mentor_name = mentor_name

    matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response
