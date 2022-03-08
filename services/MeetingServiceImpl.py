from compiled_protos.meeting_package import (
    Appointment, AppointmentType, CreatePlansOfActionsReply,
    ListAppointmentsReply, ListPlansOfActionsReply, PlansOfAction, ProfileType,
    TogglePlansOfActionCompletionReply)
from utils.connection_pool import ConnectionPool

meetingServiceConnectionPool = ConnectionPool()


def list5AppointmentsByUserIdImpl(userid: int, profile_type: ProfileType) -> ListAppointmentsReply:
    (conn, cur) = meetingServiceConnectionPool.acquire_from_connection_pool()

    PTypeStr = 'mentee' if profile_type == ProfileType.MENTEE else 'mentor'
    AnotherPTypeStr = 'mentor' if profile_type == ProfileType.MENTEE else 'mentee'

    SELECT_PROFILE_ID = f"SELECT * FROM {PTypeStr} WHERE accountid = %s"

    # Select from the union of ([Type, Another Attandance Name, Link, Start, Duration, Skill Name] of both Meetings and Workshops, for current userid)
    # and then filter by (time + duration > now) to list the ongoing ones.
    # then sort by start time, and take the first 5
    SELECTION_QUERY = f"""
SELECT * FROM (
    SELECT 0 AS atype, name AS another_name, link, start, duration, NULL AS skill_name
    FROM meeting
        NATURAL JOIN assignment
        JOIN {AnotherPTypeStr} ON assignment.{AnotherPTypeStr}id = {AnotherPTypeStr}.{AnotherPTypeStr}id
        JOIN account ON {AnotherPTypeStr}.accountid = account.accountid
        WHERE {PTypeStr}id = 2
    UNION SELECT 1 AS atype, NULL AS another_name, link, start, duration, name AS skill_name
    FROM workshop
        NATURAL JOIN skill
        NATURAL JOIN {PTypeStr}skill
        WHERE {PTypeStr}id = 2
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
    cur.execute(SELECTION_QUERY, (profileId,))

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


def createPlansOfActionsImpl(mentee_id: int, plansOfActionString: str) -> CreatePlansOfActionsReply:
    (conn, cur) = meetingServiceConnectionPool.acquire_from_connection_pool()
    QUERY = "INSERT INTO milestone VALUES(DEFAULT, %s, %s, false) RETURNING *;"

    cur.execute(QUERY, (mentee_id, plansOfActionString))
    result = cur.fetchone()

    success: bool = False
    plansOfAction: PlansOfAction = None

    if result is None:
        success = False
    else:
        success = True
        (mid, _, content, _) = result
        plansOfAction = PlansOfAction(mid, content)

    meetingServiceConnectionPool.release_to_connection_pool(conn, cur)
    return CreatePlansOfActionsReply(success, plansOfAction)
