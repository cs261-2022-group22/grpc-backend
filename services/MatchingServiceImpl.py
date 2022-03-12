import random

from compiled_protos.matching_package import MenteeToMentorMatchingReply
from psycopg import Connection, Cursor
from utils.connection_pool import ConnectionPool

matchingServiceConnectionPool = ConnectionPool()

MATCHED_MENTOR_QUERY = """
SELECT Account.accountId, Account.name 
FROM Assignment
    NATURAL JOIN Mentor 
    NATURAL JOIN Account 
WHERE Assignment.menteeId = %s;
"""

MODEL_QUERY = """
SELECT skillOverlapCoefficient, ageDifferenceCoefficient, ModelOffset 
FROM RatingModel 
WHERE businessarea1id = %s AND businessarea2id = %s; 
"""

MENTOR_SKILLS_QUERY = """
SELECT skillId 
FROM Mentor 
    NATURAL JOIN MentorSkill 
WHERE Mentor.mentorId = %s;
"""

MENTEE_SKILLS_QUERY = """
SELECT skillId 
FROM Mentee 
    NATURAL JOIN MenteeSkill 
WHERE Mentee.menteeid = %s;
"""

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
SELECT_MENTOR_BASED_ON_DIFFERENT_BUSINESS_SECTOR = """
WITH mentor_assignment_count AS (
    SELECT mentorid, COUNT(mentorid) as assignment_count
    FROM mentor
        NATURAL LEFT JOIN assignment
    GROUP BY mentorid)
SELECT mentorid, name, businesssectorid, dob 
FROM mentor_assignment_count
    NATURAL JOIN mentor
    NATURAL JOIN account
    NATURAL LEFT JOIN businesssector
WHERE
    mentor_assignment_count.assignment_count < 5 AND
    businesssectorid <> %s;
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


def selectOptimalMentor(menteeId, menteeDob, menteeBusinessAreaId, mentors, cur):
    cur.execute(MENTEE_SKILLS_QUERY, (menteeId,))
    # expose the skill ids into a set
    menteeSkills = set(map(lambda e: e[0], cur.fetchall()))

    # add the skills a mentor has to the end of their tuple
    temp = []
    for mentor in mentors:
        cur.execute(MENTOR_SKILLS_QUERY, (mentor[0],))
        mentorSkills = set(map(lambda e: e[0], cur.fetchall()))
        temp.append((*mentor, mentorSkills))

    mentors = temp

    # determine the distinct mentor business areas
    distinctMentorBusinessAreaIds = set()
    for mentor in mentors:
        distinctMentorBusinessAreaIds.add(mentor[2])

    # create dict from the distinct mentor business areas to the models
    modelDict = {}
    for distinctMentorBusinessAreaId in distinctMentorBusinessAreaIds:
        # models store the business area ids in ascending order so we must match this scheme.
        businessArea1Id, businessArea2Id = sorted([menteeBusinessAreaId, distinctMentorBusinessAreaId])
        cur.execute(MODEL_QUERY, (businessArea1Id, businessArea2Id))
        if (model := cur.fetchone()) is not None:
            modelDict[distinctMentorBusinessAreaId] = model

    # mentors for which there exists a model (that corresponds to their business area)
    known = []

    # mentors for which there doesn't exist a model
    unknown = []

    # determine for each mentor if a model exists for their business area
    # if so add them with their predicted rating with the mentee to known
    # otherwise just add their basic details to unknown
    for mentor in mentors:
        mentorBasicDetails = (mentor[0], mentor[1])
        if mentor[2] in modelDict:
            model = modelDict[mentor[2]]
            predictedRatingWithMentee = len(mentor[4] & menteeSkills)*model[0] + round((menteeDob - mentor[3]).days / 365)*model[1] + model[2]
            known.append((*mentorBasicDetails, predictedRatingWithMentee))
        else:
            unknown.append(mentorBasicDetails)

    # prefer to select an unknown situation so that data can be collected on this in the future (with ratings)
    if len(unknown) > 0:
        return random.choice(unknown)
    else:  # choose the expected best mentor
        known.sort(key=lambda e: e[2], reverse=True)
        selectedMentorWithMetric = known[0]  # exclude metric as we only care about their basic details in the return
        return (selectedMentorWithMetric[0], selectedMentorWithMetric[1])


def getMatchingMentorImpl(menteeUserId: int) -> MenteeToMentorMatchingReply:
    (conn, cur) = matchingServiceConnectionPool.acquire_from_connection_pool()

    response = MenteeToMentorMatchingReply()
    response.status = False  # failure-biased

    # retrieve mentee id
    cur.execute("SELECT menteeId FROM Mentee WHERE accountId = %s;", (menteeUserId,))
    menteeId = cur.fetchone()[0]

    # find the user id and name of the mentor they are matched to
    cur.execute(MATCHED_MENTOR_QUERY, (menteeId,))
    matchedMentorDetails = cur.fetchone()
    if matchedMentorDetails is None:
        matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
        return response

    (mentor_user_id, mentor_name) = matchedMentorDetails
    response.mentor_user_id = mentor_user_id
    response.mentor_name = mentor_name
    response.status = True

    matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def tryMatchImpl(menteeUserId: int) -> MenteeToMentorMatchingReply:
    (conn, cur) = matchingServiceConnectionPool.acquire_from_connection_pool()
    response = tryMatchImplImpl(cur, menteeUserId)
    matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def tryMatchImplImpl(cur: Cursor, menteeUserId: int) -> MenteeToMentorMatchingReply:
    response = MenteeToMentorMatchingReply()
    response.status = False  # failure-biased

    # Step 0: Get the mentee id from the given user id
    cur.execute("SELECT menteeId FROM Mentee WHERE accountId = %s;", (menteeUserId,))
    menteeId = cur.fetchone()[0]

    # Step 1: Figure out the businessArea of current mentee
    cur.execute(MENTEE_INFO_QUERY_STRING, (menteeId,))
    result = cur.fetchone()
    if result is None:
        print("Error: No such mentee:", menteeId)
        return response

    (menteeDob, _, menteeBusinessAreaId, assignments_count) = result

    if assignments_count > 1:
        print("FATAL DATABASE ERROR: REQUIREMENT 'C3.2' BROKEN")
        return response

    if assignments_count == 1:
        print("Error: Trying to match mentee for one who has one mentor assigned already.")
        return response

    # Step 2: Choose a mentor in a different one using the models.
    cur.execute(SELECT_MENTOR_BASED_ON_DIFFERENT_BUSINESS_SECTOR, (menteeBusinessAreaId,))
    mentors = cur.fetchall()
    if len(mentors) == 0:
        return response

    (mentor_id, mentor_name) = selectOptimalMentor(menteeId, menteeDob, menteeBusinessAreaId, mentors, cur)

    # Step 3: Determine the user id of the mentor.
    cur.execute("SELECT accountId FROM Mentor WHERE mentorId = %s;", (mentor_id,))
    mentor_user_id = cur.fetchone()[0]

    response.mentor_user_id = mentor_user_id
    response.mentor_name = mentor_name
    response.status = True

    cur.execute("INSERT INTO Assignment(mentorId, menteeId) VALUES(%s, %s);", (mentor_id, menteeId))
    return response
