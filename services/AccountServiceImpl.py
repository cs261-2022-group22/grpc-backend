import string
from datetime import datetime
from logging import error
from typing import List, Optional

import bcrypt
import psycopg
from compiled_protos.account_package import (AuthenticateReply, BusinessArea,
                                             GetMenteesReply,
                                             ListBusinessAreasReply,
                                             ListSkillsReply, Mentee,
                                             NotificationsReply, ProfileSignupReply, ProfilesReply,
                                             ProfileType, RegistrationReply,
                                             Skill,
                                             UpdateProfileDetailsResponse)
from utils.connection_pool import ConnectionPool

accountServiceConnectionPool = ConnectionPool()


def tryLoginImpl(username: str, password: str) -> AuthenticateReply:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    response = AuthenticateReply()
    response.status = False  # failure biased

    ###
    cur.execute("SELECT passwordHash, accountId FROM Account WHERE email=%s;", (username,))
    if (resultRow := cur.fetchone()) is not None:
        storedPasswordHashBytes = resultRow[0]
        givenPasswordPlainBytes = password.encode("utf-8")
        if bcrypt.checkpw(givenPasswordPlainBytes, storedPasswordHashBytes):
            response.id = resultRow[1]
            response.status = True
    ###

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def registerUserImpl(name: str, date_of_birth: datetime, email: str, password: str, business_area_id: int):
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    response = RegistrationReply()
    response.status = False  # failure biased

    if (len(password) < 6) or (date_of_birth.date() > datetime.now().date()) or (business_area_id <= 0) or (len(name) == 0) or (len(email) == 0):
        response.status = False
        response.account_id = None
    else:
        try:
            passwordHash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            cur.execute("""INSERT INTO public.account (accountid, name, email, passwordhash, dob, businesssectorid)
                           VALUES (DEFAULT, %s::varchar, %s::varchar, %s::bytea, %s::date, %s::integer) RETURNING accountid;""",
                        (name, email, passwordHash, date_of_birth, business_area_id))

            accountId = cur.fetchone()[0]
            print(f'CreateUser: {cur.rowcount} row affected, inserted rowid {accountId}')
            response.status = True
            response.account_id = accountId
        except psycopg.DatabaseError as e:
            error(f'CreateUser: {e}')
            response.status = False
            response.account_id = None
            conn.rollback()

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def accountProfilesImpl(userid: int) -> ProfilesReply:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    response = ProfilesReply()
    response.is_mentor = False  # failure biased
    response.is_mentee = False

    ###
    cur.execute("SELECT mentorId FROM Mentor WHERE accountId=%s;", (userid,))
    if cur.fetchone() is not None:
        response.is_mentor = True

    cur.execute("SELECT menteeId FROM Mentee WHERE accountId=%s;", (userid,))
    if cur.fetchone() is not None:
        response.is_mentee = True
    ###

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def listBusinessAreasImpl() -> ListBusinessAreasReply:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    response = ListBusinessAreasReply()
    cur.execute("SELECT * FROM businesssector;")
    results = cur.fetchall()

    for result in results:
        response.business_areas.append(BusinessArea(result[0], result[1]))

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def listSkillsImpl() -> ListSkillsReply:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    response = ListSkillsReply()
    cur.execute("SELECT * FROM skill;")
    results = cur.fetchall()

    for result in results:
        response.skills.append(Skill(result[0], result[1]))

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def getNotificationsImpl(userid: int, targetProfileType: ProfileType) -> NotificationsReply:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    profileTableIdName = "menteeid" if targetProfileType == ProfileType.MENTEE else "mentorid"
    profileTableName = "Mentee" if targetProfileType == ProfileType.MENTEE else "Mentor"
    profileMessagesTableName = "MenteeMessage" if targetProfileType == ProfileType.MENTEE else "MentorMessage"

    response = NotificationsReply()
    cur.execute(f"SELECT {profileTableIdName} FROM {profileTableName} WHERE accountid = %s;", (userid,))
    result = cur.fetchone()
    if result is None:
        accountServiceConnectionPool.release_to_connection_pool(conn, cur)
        return response

    profileId = result[0]

    cur.execute(f"SELECT message FROM {profileMessagesTableName} WHERE {profileTableIdName} = %s;", (profileId,))
    notificationResults = cur.fetchall()
    for notificationResult in notificationResults:
        response.desired_notifications.append(notificationResult[0])

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def registerProfileImpl(userid: int, desiredSkills: list[str], profileTableName: str):
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    profileTableIdName = profileTableName.lower() + "Id"
    response = ProfileSignupReply()

    cur.execute(f"SELECT * FROM {profileTableName} WHERE accountId = %s;", (userid,))
    if cur.fetchone() is not None:  # cannot have two profiles of the same type
        response.status = False
    else:  # signup a profile
        # create the profile
        cur.execute(f"INSERT INTO {profileTableName}(accountId) VALUES(%s) RETURNING {profileTableIdName};", (userid,))
        profileId = cur.fetchone()[0]
        for skillName in desiredSkills:  # add the desired skills
            cur.execute("SELECT skillId FROM Skill WHERE name = %s;", (skillName,))
            skillId = cur.fetchone()[0]
            cur.execute(f"INSERT INTO {profileTableName}Skill({profileTableIdName},skillId) VALUES(%s,%s);", (profileId, skillId))
        response.status = True

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return response


def getMenteesByMentorIdImpl(mentor_user_id: int) -> GetMenteesReply:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    QUERY_STRING = """
WITH mentorIdResult AS (SELECT mentorid FROM mentor NATURAL JOIN account WHERE accountid = %s)
SELECT mentee.accountid, name FROM assignment
    NATURAL INNER JOIN mentorIdResult
    JOIN mentee on assignment.menteeid = mentee.menteeid
    JOIN account a on mentee.accountid = a.accountid;
"""
    cur.execute(QUERY_STRING, (mentor_user_id,))

    response = []
    for result in cur.fetchall():
        response.append(Mentee(result[0], result[1]))

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return GetMenteesReply(response)


def updateProfileDetailsImpl(userid: int, profile_type: ProfileType, new_email: Optional[str], new_bs_id: Optional[int], skills: Optional[List[int]]) -> UpdateProfileDetailsResponse:
    (conn, cur) = accountServiceConnectionPool.acquire_from_connection_pool()

    print(f"UpdateProfileDetailsImpl: user: {userid}, type: {profile_type}, email: {new_email}, newbs: {new_bs_id}, skills: {skills}")

    success = False

    try:
        # The profile type of current user
        profileTypeStr = "mentee" if profile_type == ProfileType.MENTEE else "mentor"

        otherProfileTypeStr = "mentor" if profile_type == ProfileType.MENTEE else "mentee"

        # Assumed given user id is valid
        cur.execute(f"SELECT {profileTypeStr}id FROM {profileTypeStr} WHERE accountid = %s;", (userid,))
        profileId = cur.fetchone()[0]

        if new_email is not None:
            print(f" -> Updating email address for user {userid}")
            cur.execute("UPDATE account SET email = %s WHERE accountid = %s;", (new_email, userid))

        if skills is not None:
            cur.execute(f"DELETE FROM {profileTypeStr}skill WHERE {profileTypeStr}id = %s;", (profileId,))

            print(f" -> Updating Skills for user {userid}")
            for newSkill in skills:
                cur.execute(f"INSERT INTO {profileTypeStr}skill VALUES (DEFAULT, %s, %s);", (profileId, newSkill))

        if new_bs_id is not None:
            print(f" -> Updating Business Area for user {userid}")

            # Step 1 - Check which of the assignments were affected
            AFFECTED_ASSIGNMENTS = f"""
SELECT assignmentid, {otherProfileTypeStr}.{otherProfileTypeStr}id, name FROM assignment
    NATURAL JOIN {otherProfileTypeStr}
    JOIN account on {otherProfileTypeStr}.accountid = account.accountid
WHERE assignment.{profileTypeStr}id = %s    -- Current User's Profile ID
  AND account.businesssectorid = %s;        -- Business Area ID to be changed to, use '=' to select conflicted
"""
            cur.execute(AFFECTED_ASSIGNMENTS, (profileId, new_bs_id))

            for affected in cur.fetchall():
                (assignmentId, affectedProfileId, affectedName) = affected
                print(f"     -> Affected {otherProfileTypeStr}: {affectedName} (profile id: {affectedProfileId}), from assignment {assignmentId}")

                # Step 2 - Remove such assignment
                cur.execute("DELETE FROM assignment WHERE assignmentid = %s;", (assignmentId,))

                # Step 3 - Send notifications to this user:
                MESSAGE = f"""Hello {affectedName}, your {profileTypeStr} has changed their business area, as a result you have been unassigned with them."""
                cur.execute(f"INSERT INTO {otherProfileTypeStr}message VALUES(DEFAULT, %s, %s);", (affectedProfileId, MESSAGE))

            # Finally, update this
            cur.execute("UPDATE account SET businesssectorid = %s WHERE accountid = %s;", (new_bs_id, userid))

        success = True
    except Exception as e:
        print(e)
        conn.rollback()

    accountServiceConnectionPool.release_to_connection_pool(conn, cur)
    return UpdateProfileDetailsResponse(success)
