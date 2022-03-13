import asyncio
import datetime
import random
import string
import unittest
import psycopg
from psycopg import Error

from grpclib.client import Channel

import compiled_protos.account_package as AccountPackage


# Testing try_login
class TestTryLogin(unittest.TestCase):
    def test_login_success(self):  # Success login case
        # channel = Channel(host="127.0.0.1", port=50051)
        # service = AccountPackage.AccountServiceStub(channel)

        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.try_login(username="test@gmail.com", password="test"))

        print("test_login_success: ", response)
        self.assertTrue(response.status, "Testing login success failed, Expected: response.status = True")

        # channel.close()

    def test_login_failure(self):  # Failure login case
        # channel = Channel(host="127.0.0.1", port=50051)
        # service = AccountPackage.AccountServiceStub(channel)

        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.try_login(username="FalseCredentialUsername", password="FalseCredentialPassword"))

        print("test_login_failure: ",response)
        self.assertFalse(response.status, "Testing login failure failed, Expected: response.status = False")

        # channel.close()

# Testing register_user, should also add roles to this


class TestRegisterUser(unittest.TestCase):
    def test_register_invalid_password(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(2001, 2, 1), email="email", password="pa", business_area_id=1))

        print("test_register_invalid_password: ",response)
        self.assertFalse(response.status, "Testing invalid password registration, Expected: response.status = False")

    def test_register_invalid_name(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="", date_of_birth=datetime.datetime(2001, 2, 1), email="email", password="password", business_area_id=1))

        print("test_register_invalid_name: ",response)
        self.assertFalse(response.status, "Testing invalid name registration, Expected: response.status = False")

    def test_register_invalid_dob(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(3000, 2, 1), email="email", password="password", business_area_id=1))

        print("test_register_invalid_dobL:",response)
        self.assertFalse(response.status, "Testing invalid dob registration, Expected: response.status = False")

    def test_register_invalid_email(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(2001, 2, 1), email="", password="password", business_area_id=1))

        print("test_register_invalid_email",response)
        self.assertFalse(response.status, "Testing invalid email registration, Expected: response.status = False")

    def test_register_invalid_password(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(2001, 2, 1), email="email", password="password", business_area_id=-1))

        print("test_register_invalid_password",response)
        self.assertFalse(response.status, "Testing invalid business area id registration, Expected: response.status = False")

    # Test pre-existing registration
    def test_preexisting_registration(self):
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(2001, 2, 1), email="test@gmail.com", password="password", business_area_id=1))

        print("test_preexisting_registration: ",response)
        self.assertFalse(response.status, "Testing registration for pre-existing user, Expected: response.status = False")

    def test_register_success(self):
        randomstring = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        print(randomstring)
        randomemail = randomstring + "@gmail.com"
        print(randomemail)
        response = loop.run_until_complete(service.register_user(name="testname", date_of_birth=datetime.datetime(2001, 2, 1), email=randomemail, password="password", business_area_id=1))

        print("test_register_success: ",response)
        self.assertTrue(response.status, "Testing registration of valid user w/ randomly generated email, Expected: response.status = True")
        # Either need to delete original user from database or generate some random client


class TestAccountProfiles(unittest.TestCase):
    def test_is_mentor_true(self):
        response = loop.run_until_complete(service.account_profiles(userid=20))

        print("test_is_mentor_true: ",response)
        self.assertTrue(response.is_mentor, "Testing account profile userid = 20, Expected: response.is_mentor = True")
        # self.assertFalse(response.is_mentee, "Testing account profile userid = 20, Expected: response.is_mentee = False")

    def test_is_mentee_true(self):
        response = loop.run_until_complete(service.account_profiles(userid=41))

        print("test_is_mentee_true: ",response)
        self.assertTrue(response.is_mentee, "Testing account profile userid = 41, Expected: response.is_mentee = True")
        # self.assertFalse(response.is_mentor, "Testing account profile userid = 41, Expected: response.is_mentor = False")

    def test_is_mentor_failure(self):
        response = loop.run_until_complete(service.account_profiles(userid=56))

        print("test_is_mentor_failure: ",response)
        self.assertFalse(response.is_mentor, "Testing account profile userid = 56, Expected: response.is_mentor = False")

    def test_is_mentee_failure(self):
        response = loop.run_until_complete(service.account_profiles(userid=4))

        print("test_is_mentee_failure: ",response)
        self.assertFalse(response.is_mentee, "Testing account profile userid = 4, Expected: response.is_mentee = False")


class TestListBusinessAreas(unittest.TestCase):
    def test_list_business_areas(self):
        response = loop.run_until_complete(service.list_business_areas())

        print("test_list_business_areas: ",response)
        self.assertEqual(response.business_areas, [AccountPackage.BusinessArea(id=1, name='Private Bank'), AccountPackage.BusinessArea(id=2, name='Corporate Bank'), AccountPackage.BusinessArea(id=3, name='Asset Management'), AccountPackage.BusinessArea(
            id=4, name='Investment Bank')], "Testing business areas function, Expected: response.business_areas = [BusinessArea(id=1, name='Private Bank'), BusinessArea(id=2, name='Corporate Bank'), BusinessArea(id=3, name='Asset Management'), BusinessArea(id=4, name='Investment Bank')]")


class TestSkillsListing(unittest.TestCase):
    def test_skills_listing(self):
        response = loop.run_until_complete(service.list_skills())

        print("test_skills_listing: ",response)
        self.assertEqual(response.skills, [AccountPackage.Skill(id=1, name='Technical'),    AccountPackage.Skill(id=2, name='How To Progress Career'), AccountPackage.Skill(id=3, name='Management'), AccountPackage.Skill(id=4, name='Leadership'), AccountPackage.Skill(
            id=5, name='Healthy Work-Life balance')], "Testing list skills function, Expeted: response.skills = [Skill(id=1, name='Technical'), Skill(id=2, name='How To Progress Career'), Skill(id=3, name='Management'), Skill(id=4, name='Leadership'), Skill(id=5, name='Healthy Work-Life balance')]")


class TestNotifications(unittest.TestCase):  # Ask about this test
    def test_notis(self):
        # response = loop.run_until_complete(service.get_notifications(userid=41, target_profile_type=0))

        # print(response)
        # self.assertEqual(response.desired_notifications, [
        #                  'Message to mentee_1: Resource put white beyond great summer speak. Surface month interview move history. Material already church.\r\nReflect set sound measure per a. Contain rise miss between sort list set.'], "Testing notification retrieval, Expected: Notification")
        randomstring = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        print(randomstring)
        randomemail = randomstring + "@gmail.com"
        print(randomemail)
        response1 = loop.run_until_complete(service.register_user(name="testname", date_of_birth=datetime.datetime(2001, 2, 1), email=randomemail, password="password", business_area_id=1))
        uid = response1.account_id
        print("test_notis response1: ",response1)

        response2 = loop.run_until_complete(service.register_mentor(userid=uid, desired_skills=[]))
        print("test_notis response2: ",response2)

        cursor.execute("SELECT mentorId FROM Mentor WHERE accountId = %s", (uid,))
        mentorid = cursor.fetchone()[0]
        print("MENTEE ID: ",mentorid)

        cursor.execute("INSERT INTO MentorMessage (mentorId, message) VALUES (%s, %s)", (mentorid, 'This is a test massage'))
        connection.commit()

        response3 = loop.run_until_complete(service.get_notifications(userid=uid,target_profile_type=1))
        self.assertEqual(response3.desired_notifications, [
                         'This is a test massage'], "Testing notification retrieval, Expected: Notification = [This is a test massage]")

    # def test_empty_notis(self):
    #     response = loop.run_until_complete(service.get_notifications(userid=20, target_profile_type=1))

    #     print(response)
    #     self.assertEqual(response, AccountPackage.NotificationsReply(), "Testing empty notification set, Expected empty NotificationsReply()")


class TestRegisterRoles(unittest.TestCase):
    def test_register_mentor(self):
        randomstring = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        print(randomstring)
        randomemail = randomstring + "@gmail.com"
        print(randomemail)
        response1 = loop.run_until_complete(service.register_user(name="testname", date_of_birth=datetime.datetime(2001, 2, 1), email=randomemail, password="password", business_area_id=1))
        uid = response1.account_id
        print("test_register_mentor response1: ",response1)

        response2 = loop.run_until_complete(service.register_mentor(userid=response1.account_id, desired_skills=[]))

        print("test_register_mentor response2: ", response2)

        response3 = loop.run_until_complete(service.account_profiles(userid=uid))
        print("test_register_mentor response3: ", response3)
        self.assertTrue(response3.is_mentor, "Testing mentor registration, Expected: response3.is_mentor = True")

    def test_register_mentee(self):
        randomstring = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        print(randomstring)
        randomemail = randomstring + "@gmail.com"
        print(randomemail)
        response1 = loop.run_until_complete(service.register_user(name="testname", date_of_birth=datetime.datetime(2001, 2, 1), email=randomemail, password="password", business_area_id=1))
        uid = response1.account_id
        print("test_register_mentee response1: ",response1)

        response2 = loop.run_until_complete(service.register_mentee(userid=response1.account_id, desired_skills=[]))

        print("test_register_mentee response2: ",response2)

        response3 = loop.run_until_complete(service.account_profiles(userid=uid))
        print("test_register_mentee response3: ",response3)
        self.assertTrue(response3.is_mentee, "Testing mentee registration, Expected: response3.is_mentee = True")


# Tests runs on same channel connections
channel = Channel(host="127.0.0.1", port=50051)
service = AccountPackage.AccountServiceStub(channel)
loop = asyncio.get_event_loop_policy().get_event_loop()

try:
    # connection = psycopg.connect(user="cs261",password="cs261-group22",host="20.77.8.229",port="5432", database="mentoring")
    connection = psycopg.connect("user=cs261 password=cs261-group22 hostaddr=20.77.8.229 port=5432 dbname=mentoring")
    cursor = connection.cursor()

except (Exception, Error) as error:
    print("Error connecting to database", error)

if __name__ == '__main__':
    unittest.main()

channel.close()
cursor.close()
connection.close()