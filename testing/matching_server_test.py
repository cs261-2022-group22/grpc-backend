import asyncio
from grpclib.client import Channel
import compiled_protos.matching_package as MatchingPackage
from compiled_protos.matching_package import MenteeToMentorMatchingReply
import compiled_protos.account_package as AccountPackage
import unittest
import datetime
import random
import string
import psycopg
from psycopg import Error
import bcrypt

class TestSelectOptimalMentor(unittest.TestCase):
    def test_selection_failure_c3point2(self):
        response = loop.run_until_complete(service.try_match(mentee_user_id=1))

        print(response)
        # self.assertEqual(response, MenteeToMentorMatchingReply(),"Testing selection for previously assigned mentee, Expected: response = GetMatchingReply()")
        self.assertFalse(response.status, "Testing selection invalid mentee user id, Expected: response.status = False")

    # def test_selection_failure_invalid_id(self):
    #     randomstring = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 10))
    #     print(randomstring)
    #     randomemail = randomstring + "@gmail.com"
    #     print(randomemail)

    #     passwordHash = bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt())

    #     cursor.execute("INSERT INTO Account (name, email, passwordHash, dob, businessSectorId) VALUES (%s,%s,%s,%s,%s) RETURNING accountId",("Test", randomemail, passwordHash, datetime.datetime(2001,2,1), 2))
    #     userid = cursor.fetchone()[0]
    #     print(userid)
    #     connection.commit()
    #     response = loop.run_until_complete(service.try_match(mentee_user_id=userid))

    #     print(response)
    #     # self.assertEqual(response, MenteeToMentorMatchingReply(),"Testing selection invalid mentee_id, Expected: response = GetMatchingReply()")
    #     self.assertFalse(response.status, "Testing selection invalid mentee user id, Expected: response.status = False")

    def test_selection_success(self):
        randomstring = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 10))
        print(randomstring)
        randomemail = randomstring + "@gmail.com"
        print(randomemail)

        passwordHash = bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO Account (name, email, passwordHash, dob, businessSectorId) VALUES (%s,%s,%s,%s,%s) RETURNING accountId",("Test", randomemail, passwordHash, datetime.datetime(2001,2,1), 2))
        userid = cursor.fetchone()[0]
        print(userid)
        connection.commit()

        cursor.execute("INSERT INTO Mentee (accountId) VALUES (%s) RETURNING menteeId", (userid,))
        menteeid = cursor.fetchone()[0]
        print(menteeid)
        connection.commit()

        response = loop.run_until_complete(service.try_match(mentee_user_id=userid))

        cursor.execute("SELECT businessSectorId FROM Account WHERE accountId = %s", (userid,))
        menteeBusinessId = cursor.fetchone()[0]

        cursor.execute("SELECT businessSectorId FROM Account WHERE accountId = (SELECT accountId FROM Mentor WHERE mentorId = (SELECT mentorId FROM Assignment WHERE menteeId = %s))", (menteeid,))
        mentorBusinessId = cursor.fetchone()[0]

        print(response)
        self.assertNotEqual(menteeBusinessId, mentorBusinessId, "Testing valid pairing, Expected; Mentor and mentee should have different business areas")

class TestGetMatchingMentor(unittest.TestCase):
    def get_matching_mentor_success(self):
        response = loop.run_until_complete(service.get_matching_mentor(mentee_user_id=1))

        print(response)
        self.assertEqual(response.mentor_user_id, 43,"Testing get matching mentor function, Expected: response.mentee_user_id = 43")
        # self.assertFalse(response.status, "Testing selection invalid mentee user id, Expected: response.status = False")

    # def get_matching_mentor_failure(self):
    #     response = loop.run_until_complete(service.get_matching_mentor(mentee_user_id=74))

    #     print(response)
    #     self.assertFalse(response.status,"Testing get matching mentor function failure, Expected: user_id = 74, response.status = False")

# Tests runs on same channel connections
channel = Channel(host="127.0.0.1", port=50051)
service = MatchingPackage.MatchingServiceStub(channel)
# tempservice = AccountPackage.AccountServiceStub(channel)
loop = asyncio.get_event_loop_policy().get_event_loop()

try:
    # connection = psycopg.connect(user="cs261",password="cs261-group22",host="20.77.8.229",port="5432", database="mentoring")
    connection = psycopg.connect("user=cs261 password=cs261-group22 hostaddr=20.77.8.229 port=5432 dbname=mentoring")
    cursor = connection.cursor()

except (Exception, Error) as error:
    print("Error connecting to database", error)

if __name__  == '__main__':
    unittest.main()
    
channel.close()
cursor.close()
connection.close()
