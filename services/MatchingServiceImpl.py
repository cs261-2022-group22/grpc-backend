import random
from compiled_protos.matching_package import GetMatchingMentorReply
from utils.connection_pool import ConnectionPool

matchingServiceConnectionPool = ConnectionPool()

MENTEE_INFO_QUERY_STRING = """
SELECT dob, accountid, businesssectorid, COUNT(assignmentid) AS assignments_count
FROM mentee
    NATURAL JOIN account
    NATURAL LEFT JOIN businesssector
    NATURAL LEFT OUTER JOIN assignment
WHERE menteeid = %s
GROUP BY dob, accountid, businesssectorid;
"""

# TODO: Better matching, based on DoB, feedback metrics, skills
SELECT_MENTOR_BASED_ON_MATCHING_BUSINESS_SECTOR = """
WITH mentor_assignment_count AS (
    SELECT mentorid, COUNT(mentorid) as assignment_count
    FROM mentor
        NATURAL LEFT JOIN assignment
    GROUP BY mentorid)
SELECT mentorid, name
FROM mentor_assignment_count
    NATURAL JOIN mentor
    NATURAL JOIN account
    NATURAL LEFT JOIN businesssector
WHERE
    mentor_assignment_count.assignment_count < 5 AND
    businesssectorid = %s;
"""

# #
# - C3.1: The pairings of the mentor to mentee will be appropriate based on a variety of factors and once paired, the system will reflect this.
# V C3.2: The mentor will have up to 5 mentees,
# V       and a mentee will only have one mentor.
# - D3.1: The system will use machine learning techniques and user data to generate possible pairings. Data used for consideration:
# V Business Sectors and
# - Skills of both mentee and mentor
# - Expertise level of mentor
# - Miscellaneous factors such as workload - e.g. number of assigned mentees
# - Age difference between mentor and mentee
# - Current mentor and mentee star rating
# - Mentee development feedback from mentor. This will be processed with sentiment analysis
# - Justification: Machine learning allows for improvements to more accurate pairings in the future, which addresses poor matches that users receive.
# #


def getMatchingMentorImpl(menteeId: int) -> GetMatchingMentorReply:
    (conn, cur) = matchingServiceConnectionPool.acquire_from_connection_pool()

    # Step 1: Figure out the businessArea of current mentee
    cur.execute(MENTEE_INFO_QUERY_STRING, (menteeId,))
    result = cur.fetchone()
    if result is None:
        print("Error: No such mentee:", menteeId)
        return GetMatchingMentorReply()

    (_, _, bussinessAreaId, assignments_count) = result

    if assignments_count > 1:
        print("FATAL DATABASE ERROR: REQUIREMENT 'C3.2' BROKEN")
        return GetMatchingMentorReply()

    if assignments_count == 1:
        print("Error: Trying to match mentor for one who has one mentor assigned already.")
        return GetMatchingMentorReply()

    # Step 2: RANDOMLY choose a mentor on this
    cur.execute(SELECT_MENTOR_BASED_ON_MATCHING_BUSINESS_SECTOR, (bussinessAreaId,))
    mentors = cur.fetchall()
    (mentor_id, mentor_name) = random.choice(mentors)

    response = GetMatchingMentorReply()
    response.mentor_id = mentor_id
    response.mentor_name = mentor_name

    matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response
