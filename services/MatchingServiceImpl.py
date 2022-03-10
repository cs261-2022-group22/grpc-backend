import random
from compiled_protos.matching_package import GetMatchingMentorReply
from utils.connection_pool import ConnectionPool

matchingServiceConnectionPool = ConnectionPool()

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
SELECT_MENTOR_BASED_ON_MATCHING_BUSINESS_SECTOR = """
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
        cur.execute(MODEL_QUERY, (menteeBusinessAreaId, distinctMentorBusinessAreaId))
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


def getMatchingMentorImpl(menteeId: int) -> GetMatchingMentorReply:
    (conn, cur) = matchingServiceConnectionPool.acquire_from_connection_pool()

    # Step 1: Figure out the businessArea of current mentee
    cur.execute(MENTEE_INFO_QUERY_STRING, (menteeId,))
    result = cur.fetchone()
    if result is None:
        print("Error: No such mentee:", menteeId)
        matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
        return GetMatchingMentorReply()

    (menteeDob, _, menteeBusinessAreaId, assignments_count) = result

    if assignments_count > 1:
        print("FATAL DATABASE ERROR: REQUIREMENT 'C3.2' BROKEN")
        matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
        return GetMatchingMentorReply()

    if assignments_count == 1:
        print("Error: Trying to match mentor for one who has one mentor assigned already.")
        matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
        return GetMatchingMentorReply()

    # Step 2: RANDOMLY choose a mentor on this
    cur.execute(SELECT_MENTOR_BASED_ON_MATCHING_BUSINESS_SECTOR, (menteeBusinessAreaId,))
    mentors = cur.fetchall()
    if len(mentors) == 0:
        matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
        return GetMatchingMentorReply()

    response = GetMatchingMentorReply()
    (mentor_id, mentor_name) = selectOptimalMentor(menteeId, menteeDob, menteeBusinessAreaId, mentors, cur)
    response.mentor_id = mentor_id
    response.mentor_name = mentor_name

    cur.execute("INSERT INTO Assignment(mentorId, menteeId) VALUES(%s, %s);", (mentor_id, menteeId))

    matchingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response
