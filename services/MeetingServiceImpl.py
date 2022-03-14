from datetime import datetime

from compiled_protos.meeting_package import (
    Appointment, AppointmentType, CreatePlansOfActionsReply,
    ListAppointmentsReply, ListPlansOfActionsReply, PlansOfAction, ProfileType,
    ScheduleNewMeetingReply, ScheduleNewWorkshopReply,
    TogglePlansOfActionCompletionReply)
from utils.connection_pool import ConnectionPool

meetingServiceConnectionPool = ConnectionPool()


def list5AppointmentsByUserIdImpl(userid: int, profile_type: ProfileType) -> ListAppointmentsReply:
    (conn, cur) = meetingServiceConnectionPool.acquire_from_connection_pool()

    PTypeStr = 'mentee' if profile_type == ProfileType.MENTEE else 'mentor'
    OtherPTypeStr = 'mentor' if profile_type == ProfileType.MENTEE else 'mentee'

    SELECT_PROFILE_ID = f"SELECT * FROM {PTypeStr} WHERE accountid = %s"

    # Select from the union of ([Type, Other Attandance Name, Link, Start, Duration, Skill Name] of both Meetings and Workshops, for current userid)
    # and then filter by (time + duration > now) to list the ongoing ones.
    # then sort by start time, and take the first 5
    SELECTION_QUERY = f"""
SELECT * FROM (
    SELECT 0 AS atype, name AS other_name, link, start, duration, NULL AS skill_name
    FROM meeting
        NATURAL JOIN assignment
        JOIN {OtherPTypeStr} ON assignment.{OtherPTypeStr}id = {OtherPTypeStr}.{OtherPTypeStr}id
        JOIN account ON {OtherPTypeStr}.accountid = account.accountid
        WHERE {PTypeStr}id = %s
    UNION SELECT 1 AS atype, NULL AS other_name, link, start, duration, name AS skill_name
    FROM workshop
        NATURAL JOIN skill
        NATURAL JOIN {PTypeStr}skill
        WHERE {PTypeStr}id = %s
) AS T
WHERE (start + ((duration || ' minutes')::interval)) > now()::timestamp
ORDER BY start
LIMIT 5;
"""

    cur.execute(SELECT_PROFILE_ID, (userid,))
    result = cur.fetchone()

    if result is None:
        print(f"Something went wrong, provided userid {userid} is not a {PTypeStr}")
        meetingServiceConnectionPool.release_to_connection_pool(conn, cur)
        return ListAppointmentsReply()

    profileId = result[0]
    cur.execute(SELECTION_QUERY, (profileId, profileId,))

    appointments = []

    for result in cur.fetchall():
        (atype, name, link, start, duration, skill_name) = result
        appointments.append(Appointment(AppointmentType(atype), name, start, duration, skill_name, link))

    meetingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return ListAppointmentsReply(appointments)


def listPlansOfActionsImpl(userid: int) -> ListPlansOfActionsReply:
    (conn, cur) = meetingServiceConnectionPool.acquire_from_connection_pool()

    QUERY = """
SELECT milestoneid as Id, content FROM mentee
    NATURAL JOIN milestone
WHERE not completed and accountid = %s
ORDER BY milestoneid;"""

    cur.execute(QUERY, (userid,))

    results = []
    for result in cur.fetchall():
        (mid, mcontent) = result
        results.append(PlansOfAction(mid, mcontent))

    meetingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return ListPlansOfActionsReply(results)


def togglePlansOfActionCompletionImpl(plan_id: int) -> TogglePlansOfActionCompletionReply:
    (conn, cur) = meetingServiceConnectionPool.acquire_from_connection_pool()

    QUERY = "UPDATE milestone SET completed = NOT completed WHERE milestoneid = %s RETURNING *;"
    cur.execute(QUERY, (plan_id,))

    success = len(cur.fetchall()) > 0

    meetingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return TogglePlansOfActionCompletionReply(success)


def createPlansOfActionsImpl(mentee_user_id: int, plansOfActionString: str) -> CreatePlansOfActionsReply:
    (conn, cur) = meetingServiceConnectionPool.acquire_from_connection_pool()
    QUERY = "INSERT INTO milestone VALUES(DEFAULT, (SELECT menteeid FROM mentee WHERE accountid = %s), %s, false) RETURNING milestoneId, content;"

    cur.execute(QUERY, (mentee_user_id, plansOfActionString))
    result = cur.fetchone()

    success: bool = False
    plansOfAction: PlansOfAction = None

    if result is not None:
        success = True
        (mid, content) = result
        plansOfAction = PlansOfAction(mid, content)

    meetingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return CreatePlansOfActionsReply(success, plansOfAction)


def getMentorMentee(cur, menteeUserId):
    """ Determines the mentor id and mentee id for a mentee and their 
    corresponding matched mentor. Also retrieve the mentor and mentee names. """
    PROFILE_ID_QUERY = """
    SELECT Assignment.mentorId, Assignment.menteeId 
    FROM Account 
        NATURAL JOIN Mentee 
        NATURAL JOIN Assignment 
    WHERE Account.accountId = %s;
    """
    cur.execute(PROFILE_ID_QUERY, (menteeUserId,)) #retrieve ids
    mentorId, menteeId = cur.fetchone()

    #retrieve the mentor name
    MENTOR_NAME_QUERY = """
    SELECT name 
    FROM Mentor 
        NATURAL JOIN Account 
    WHERE mentorId = %s;
    """
    cur.execute(MENTOR_NAME_QUERY, (mentorId,))
    mentorName = cur.fetchone()[0]

    #retrieve the mentee name
    MENTEE_NAME_QUERY = """
    SELECT name 
    FROM Mentee 
        NATURAL JOIN Account 
    WHERE menteeId = %s;
    """
    cur.execute(MENTEE_NAME_QUERY, (menteeId,))
    menteeName = cur.fetchone()[0]

    #form result
    return (mentorId, menteeId, mentorName, menteeName)


def scheduleNewMeetingImpl(mentee_user_id: int, start: datetime, duration: int, link: str) -> ScheduleNewMeetingReply:
    (conn, cur) = meetingServiceConnectionPool.acquire_from_connection_pool()
    # Step 1: Get mentee, mentor IDs

    QUERY = """
SELECT assignmentid FROM assignment
    JOIN mentee ON assignment.menteeid = mentee.menteeid
WHERE mentee.accountid = %s;
"""
    cur.execute(QUERY, (mentee_user_id,))

    assignmentId = cur.fetchone()[0]

    # Step 2: Check possible collision, check if this assignment is busy at this time
    DETECT_COLLISION_QUERY = """
WITH Data AS (
    SELECT
        (start) AS StartTime,
        (start + ((duration || ' minutes')::interval)) AS EndTime,
        (%s) AS CheckStartTime,
        (%s + ((%s || ' minutes')::interval)) AS CheckEndTime,
        assignmentid
    FROM meeting
    NATURAL JOIN assignment
    WHERE assignmentid = %s
) SELECT * FROM Data
WHERE CheckEndTime > StartTime
  AND EndTime      > CheckStartTime
"""

    cur.execute(DETECT_COLLISION_QUERY, (start, start, duration, assignmentId))

    success = False
    if len(cur.fetchall()) == 0:
        # Step 3: Insert into the meeting table
        cur.execute("INSERT INTO meeting VALUES(DEFAULT, %s, %s, %s, %s)", (assignmentId, link, start, duration))

        # Step 4: Notify the mentor and mentee of the meeting
        mentorId, menteeId, mentorName, menteeName = getMentorMentee(cur, mentee_user_id)
        MENTOR_MEETING_NOTIFICATION = f"A meeting with {menteeName} has been scheduled from {start} for a duration of {duration} minutes."
        MENTEE_MEETING_NOTIFICATION = f"A meeting with {mentorName} has been scheduled from {start} for a duration of {duration} minutes."
        cur.execute("INSERT INTO MentorMessage(mentorId, message) VALUES(%s,%s);", (mentorId, MENTOR_MEETING_NOTIFICATION))
        cur.execute("INSERT INTO MenteeMessage(menteeId, message) VALUES(%s,%s);", (menteeId, MENTEE_MEETING_NOTIFICATION))

        success = True #done the operation

    meetingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return ScheduleNewMeetingReply(success)


def extractSingleField(givenResultSet):
    # Extracts the single field out of each record in a
    # result set (list of tuples). Hence produces a list
    # of field values.
    return list(map(lambda e: e[0], givenResultSet))


def notifyWorkshop(cur, profileTypeName, skillId, notificationMessage):
    """ Notify profiles of the given type with the notification message if 
    they are interested in a workshop of a given skill. They would be interested 
    if they desire or teach that skill. """

    profileTypeIdName = f"{profileTypeName.lower()}Id"

    # identify profiles of the given type that are interested
    INTERESTED_PROFILES = f"""
    SELECT {profileTypeIdName} 
    FROM {profileTypeName} o 
    WHERE EXISTS (
        SELECT * 
        FROM {profileTypeName}Skill 
        WHERE skillId = %s AND {profileTypeIdName} = o.{profileTypeIdName}
    );
    """
    cur.execute(INTERESTED_PROFILES, (skillId,))
    interestedProfileIds = extractSingleField(cur.fetchall())

    #notify them
    for profileId in interestedProfileIds:
        cur.execute(f"INSERT INTO {profileTypeName}Message({profileTypeIdName},message) VALUES(%s,%s);", (profileId,notificationMessage))


def scheduleNewWorkshopImpl(start: datetime, duration: int, link: str, skill: str) -> ScheduleNewWorkshopReply:
    (conn, cur) = meetingServiceConnectionPool.acquire_from_connection_pool()

    response = ScheduleNewWorkshopReply()
    response.status = False  # failure-biased

    # Step 1: Determine the skillId
    cur.execute("SELECT skillId FROM Skill WHERE name = %s;", (skill,))
    skillId = cur.fetchone()[0]

    # Step 2: Detect collisions with workshops of the same skill
    WORKSHOP_COLLISION_QUERY = """
    WITH WorkshopCollision AS (
        SELECT
            (start) AS StartTime,
            (start + ((duration || ' minutes')::interval)) AS EndTime,
            (%s) AS CheckStartTime,
            (%s + ((%s || ' minutes')::interval)) AS CheckEndTime
        FROM Workshop 
        WHERE skillId = %s
    ) SELECT * FROM WorkshopCollision
    WHERE CheckEndTime > StartTime
    AND EndTime > CheckStartTime;
    """
    cur.execute(WORKSHOP_COLLISION_QUERY, (start, start, duration, skillId))
    if cur.fetchone() is None:  # can add it if there are no collisions
        cur.execute("INSERT INTO Workshop(skillId, link, start, duration) VALUES(%s,%s,%s,%s);", (skillId, link, start, duration))

        #notify all interested profiles - mentees/mentors that desire/teach the target skill
        WORKSHOP_NOTIFICATION = f"A workshop on {skill} has been scheduled from {start} for a duration of {duration} minutes." 
        notifyWorkshop(cur, "Mentor", skillId, WORKSHOP_NOTIFICATION)
        notifyWorkshop(cur, "Mentee", skillId, WORKSHOP_NOTIFICATION)

        response.status = True  # done the operation

    meetingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response
