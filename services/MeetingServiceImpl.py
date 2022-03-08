from compiled_protos.meeting_package import (
    Appointment, AppointmentType, CreatePlansOfActionsReply,
    ListAppointmentsReply, ListPlansOfActionsReply, PlansOfAction, ProfileType,
    TogglePlansOfActionCompletionReply)
from utils.connection_pool import ConnectionPool

meetingServiceConnectionPool = ConnectionPool()


def list5AppointmentsByUserIdImpl(userid: int, profile_type: ProfileType) -> ListAppointmentsReply:
    (conn, cur) = meetingServiceConnectionPool.acquire_from_connection_pool()

    ProfileTypeStr = 'mentee' if profile_type == ProfileType.MENTEE else 'mentor'
    AnotherProfileTypeStr = 'mentor' if profile_type == ProfileType.MENTEE else 'mentee'

    SELECT_PROFILE_ID = f"SELECT * FROM {ProfileTypeStr} WHERE accountid = %s"

    SELECTION_QUERY = f"""
WITH T AS (SELECT 0 as atype, {ProfileTypeStr}id as profile_id, {AnotherProfileTypeStr}id as another_profile_id, link, start, duration, '' as skill_name
FROM meeting
    NATURAL JOIN assignment
UNION SELECT 1 as atype, {ProfileTypeStr}id as profile_id, -1, link, start, duration, name as skill_name
FROM workshop
    NATURAL JOIN skill
    NATURAL JOIN {ProfileTypeStr}skill
) SELECT atype, name, link, start, duration, skill_name
FROM T
    LEFT JOIN {AnotherProfileTypeStr} ON T.another_profile_id = {AnotherProfileTypeStr}.{AnotherProfileTypeStr}id
    LEFT JOIN account ON {AnotherProfileTypeStr}.accountid = account.accountid
WHERE (start + ((duration || ' minutes')::interval)) > now()::timestamp
    AND profile_id = %s
ORDER BY start
LIMIT 5;
"""

    cur.execute(SELECT_PROFILE_ID, (userid,))
    result = cur.fetchone()

    if result is None:
        print(f"Something went wrong, provided userid {userid} is not a {ProfileTypeStr}")
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


def togglePlansOfActionCompletionImpl(userid: int, plan_id: int) -> TogglePlansOfActionCompletionReply:
    return TogglePlansOfActionCompletionReply()


def createPlansOfActionsImpl(plans_of_action: str) -> CreatePlansOfActionsReply:
    return CreatePlansOfActionsReply()
