from compiled_protos.account_package import BusinessArea
from compiled_protos.feedback_package import (AddFeedbackReply)
from utils.connection_pool import ConnectionPool

feedbackServiceConnectionPool = ConnectionPool()

ACCOUNT_BUSINESS_SECTOR_DOB_QUERY = """
SELECT businessSectorId, dob FROM Account WHERE accountId = %s;
"""


def getBusinessAreasAscendingAgeDifference(cur, mentorUserId, menteeUserId, mentorId, menteeId, rating):
    """Get their business areas in ascending order (of id), their skill overlap 
    and their age difference. This is required by the ML system."""

    #determine the business area ids and dobs 
    cur.execute(ACCOUNT_BUSINESS_SECTOR_DOB_QUERY, (mentorUserId,))
    (mentorBaId, mentorDob) = cur.fetchone()
    cur.execute(ACCOUNT_BUSINESS_SECTOR_DOB_QUERY, (menteeUserId,))
    (menteeBaId, menteeDob) = cur.fetchone()

    #determine the age difference between the users
    ageDifference = 0

    #extract the skills of the mentor and mentee
    #determine the skill overlap as a numerical amount
    skillOverlap = 0

    #allocate the business areas in ascending order (of id)

    return sorted([mentorBaId, menteeBaId]) + [skillOverlap, ageDifference]


def addFeedbackOnMentorImpl(mentorUserId: int, menteeUserId: int, rating: float) -> AddFeedbackReply:
    (conn, cur) = feedbackServiceConnectionPool.acquire_from_connection_pool()

    response = AddFeedbackReply()
    response.status = False #failure-biased

    # Step 1: determine the mentor and mentee ids.
    #mentor id
    cur.execute("SELECT mentorId FROM Mentor WHERE accountId = %s;", (mentorUserId,))
    mentorId = cur.fetchone()[0]
    #mentee id
    cur.execute("SELECT menteeId FROM Mentee WHERE accountId = %s;", (menteeUserId,))
    menteeId = cur.fetchone()[0]

    # Step 2: determine the assignment.
    cur.execute("SELECT assignmentId FROM Assignment WHERE mentorId = %s AND menteeId = %s;", 
    (mentorId, menteeId))
    assignmentId = cur.fetchone()[0]

    # Step 3: add the feedback to the main system.
    cur.execute("INSERT INTO MentorFeedback(assignmentId, rating) VALUES(%s,%s);", 
    (assignmentId, rating))

    # Step 4: queue the feedback to be added to the machine learning system so 
    # that it can be used to improve future pairings.
    queueFeedbackForMl(cur, mentorUserId, menteeUserId, mentorId, menteeId, rating)

    #operation was successful
    response.status = True
    feedbackServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response
