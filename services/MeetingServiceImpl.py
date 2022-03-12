from datetime import datetime

from compiled_protos.meeting_package import (
    Appointment, AppointmentType, CreatePlansOfActionsReply,
    ListAppointmentsReply, ListPlansOfActionsReply, PlansOfAction, ProfileType,
    ScheduleNewMeetingReply, TogglePlansOfActionCompletionReply)
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

    # Step 2: Check possible collision, check for either the mentor or mentee is busy at this time
    DETECT_COLLISION_QUERY = """
WITH Data AS (
    SELECT
        (start) AS StartTime,
        (start + ((duration || ' minutes')::interval)) AS EndTime,
        (%s) AS CheckStartTime,
        (%s + ((%s || ' minutes')::interval)) AS CheckEndtime,
        assignmentid,
        mentorid,
        menteeid
    FROM meeting
    NATURAL JOIN assignment
    WHERE assignmentid = %s
) SELECT * FROM Data
WHERE (StartTime > CheckStartTime AND StartTime < CheckEndTime)
   OR (EndTime   > CheckStartTime AND EndTime   < CheckEndtime)
"""

    cur.execute(DETECT_COLLISION_QUERY, (start, start, duration, assignmentId))

    success = False
    if len(cur.fetchall()) == 0:
        # Step 3: Insert into the meeting table
        cur.execute("INSERT INTO meeting VALUES(DEFAULT, %s, %s, %s, %s)", (assignmentId, link, start, duration))
        success = True

    meetingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return ScheduleNewMeetingReply(success)
