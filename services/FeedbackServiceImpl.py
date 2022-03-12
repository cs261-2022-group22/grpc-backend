from compiled_protos.feedback_package import AddFeedbackReply
from utils.connection_pool import ConnectionPool

feedbackServiceConnectionPool = ConnectionPool()

ACCOUNT_BUSINESS_SECTOR_DOB_QUERY = """
SELECT businessSectorId, dob FROM Account WHERE accountId = %s;
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


def queueFeedbackForMl(cur, mentorUserId, menteeUserId, mentorId, menteeId, rating):
    """Get their business areas in ascending order (of id), their skill overlap 
    and their age difference. This is required by the ML system."""

    # determine the business area ids and dobs
    cur.execute(ACCOUNT_BUSINESS_SECTOR_DOB_QUERY, (mentorUserId,))
    (mentorBaId, mentorDob) = cur.fetchone()
    cur.execute(ACCOUNT_BUSINESS_SECTOR_DOB_QUERY, (menteeUserId,))
    (menteeBaId, menteeDob) = cur.fetchone()

    # determine the age difference between the users
    # (this should be positive if the mentee is older)
    ageDifference = round((menteeDob - mentorDob).days / 365)

    # extract the skills of the mentor and mentee
    cur.execute(MENTOR_SKILLS_QUERY, (mentorId,))
    mentorSkills = set(map(lambda e: e[0], cur.fetchall()))
    cur.execute(MENTEE_SKILLS_QUERY, (menteeId,))
    menteeSkills = set(map(lambda e: e[0], cur.fetchall()))
    # determine the skill overlap as a numerical amount
    skillOverlap = len(mentorSkills & menteeSkills)

    # allocate the business areas in ascending order (of id)
    (businessArea1Id, businessArea2Id) = sorted([mentorBaId, menteeBaId])

    # queue the feedback for the ML system with the desired format
    cur.execute("INSERT INTO PendingRatingFeedback VALUES(%s,%s,%s,%s,%s);",
                (businessArea1Id, businessArea2Id, skillOverlap, ageDifference, rating))


def ratingFeedbackExists(cur, assignmentId: int, profileName: str):
    """ Check whether matching feedback exists for the specified profile in the 
    given assignment. """
    cur.execute(f"SELECT {profileName.lower()}FeedbackId FROM {profileName}Feedback WHERE assignmentId = %s;", (assignmentId,))
    return cur.fetchone() is not None  #exists if there is some record for the desired feedback


def addRatingFeedbackImpl(profileName: str, mentorUserId: int, menteeUserId: int, rating: float) -> AddFeedbackReply:
    """ Derives the assignment from the mentor and mentee user ids given. Adds rating feedback 
    on the profile specified. Also queues the feedback to be added to the ML system after 
    computing the required metrics. """
    (conn, cur) = feedbackServiceConnectionPool.acquire_from_connection_pool()

    response = AddFeedbackReply()
    response.status = False  # failure-biased

    # Step 0: round rating to 1dp
    rating = round(rating, 1)

    # Step 1: determine the mentor and mentee ids.
    # mentor id
    cur.execute("SELECT mentorId FROM Mentor WHERE accountId = %s;", (mentorUserId,))
    mentorId = cur.fetchone()[0]
    # mentee id
    cur.execute("SELECT menteeId FROM Mentee WHERE accountId = %s;", (menteeUserId,))
    menteeId = cur.fetchone()[0]

    # Step 2: determine the assignment.
    cur.execute("SELECT assignmentId FROM Assignment WHERE mentorId = %s AND menteeId = %s;",
                (mentorId, menteeId))
    assignmentId = cur.fetchone()[0]

    # CHECK: Only 1 piece of feedback on the profile permitted per matching
    if ratingFeedbackExists(cur, assignmentId, profileName): # feedback already present so not allowed more
        feedbackServiceConnectionPool.release_to_connection_pool(conn, cur)
        return response

    # Step 3: add the feedback to the main system.
    cur.execute(f"INSERT INTO {profileName}Feedback(assignmentId, rating) VALUES(%s,%s);",
                (assignmentId, rating))

    # Step 4: queue the feedback to be added to the machine learning system so
    # that it can be used to improve future pairings.
    queueFeedbackForMl(cur, mentorUserId, menteeUserId, mentorId, menteeId, rating)

    # operation was successful
    response.status = True
    feedbackServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def addDevFeedback(content: str):
    return AddFeedbackReply()
