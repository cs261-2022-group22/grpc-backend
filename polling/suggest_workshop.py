import psycopg

from utils import GetConnectionString


def extractSingleField(givenResultSet):
    #Extracts the single field out of each record in a 
    # result set (list of tuples). Hence produces a list 
    # of field values.
    return map(lambda e: e[0], givenResultSet)


def adviseWorkshopSkill(cur, skillId, skillName):
    """ Advise mentors, that are able to, to create a workshop on the given 
    skill via the medium of notifications. """

    ADVICE_MESSAGE = f"There is high demand for the {skillName} skill. It is advised to schedule workshops on it if there are not already many on it."

    # Step 1: Determine mentors that are able to create the workshops for the 
    # desired skill - those that teach that skill.
    APPLICABLE_MENTOR_QUERY = """
    SELECT mentorId 
    FROM Mentor o 
    WHERE EXISTS(
        SELECT * FROM MentorSkill 
        WHERE 
            skillId = %s 
            AND mentorId = o.mentorId
    );
    """
    cur.execute(APPLICABLE_MENTOR_QUERY, (skillId,))
    applicableMentorIds = extractSingleField(cur.fetchall())

    # Step 2: Advise these mentors via notifications
    for mentorId in applicableMentorIds:
        #send notification
        cur.execute("INSERT INTO MentorMessage(mentorId, message) VALUES(%s,%s);", (mentorId, ADVICE_MESSAGE)) 


def SuggestWorkshop():
    conn = psycopg.connect(GetConnectionString())
    cur = conn.cursor()

    # Step 1: Determine unmatched mentees
    UNMATCHED_MENTEE_QUERY = """
    SELECT menteeId FROM Mentee o WHERE 
        NOT EXISTS (
            SELECT * FROM Assignment 
            WHERE Assignment.menteeId = o.menteeId
        );
    """
    cur.execute(UNMATCHED_MENTEE_QUERY)
    unmatchedMenteeIds = extractSingleField(cur.fetchall())

    # Step 2: Count their desired skills 
    ALL_SKILL_QUERY = """
    SELECT skillId, name FROM Skill;    
    """
    MENTEE_SKILL_QUERY = """
    SELECT skillId 
    FROM MenteeSkill 
    WHERE menteeId = %s;
    """
    skillNameMapping = {} #dictionary for the names of skills
    skillCount = {} #dictionary to count the skills
    cur.execute(ALL_SKILL_QUERY)
    for skillId, name in cur.fetchall(): 
        #initialise the count for each skill to 0
        skillCount[skillId] = 0
        #initialise the name for each skill
        skillNameMapping[skillId] = name
    
    #for each unmatched mentee
    for menteeId in unmatchedMenteeIds:
        cur.execute(MENTEE_SKILL_QUERY, (menteeId,))
        #count the skills
        for skillId in extractSingleField(cur.fetchall()):
            skillCount[skillId] += 1

    # Step 3: Determine skills that exceed threshold of subscription from 
    # unmatched mentees. Advise workshops for these skills to applicable mentors.
    for skillId, count in skillCount.items():
        if count >= 20:
            adviseWorkshopSkill(cur, skillId, skillNameMapping[skillId])

    conn.commit()

    cur.close()
    conn.close()
