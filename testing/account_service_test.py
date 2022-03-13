import asyncio
from grpclib.client import Channel
import compiled_protos.account_package as AccountPackage
import unittest
import datetime
import random
import string

# Testing try_login
class TestTryLogin(unittest.TestCase):
    def test_login_success(self): # Success login case
        # channel = Channel(host="127.0.0.1", port=50051)
        # service = AccountPackage.AccountServiceStub(channel)
        
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.try_login(username="test@gmail.com", password="test"))

        print(response)
        self.assertTrue(response.status, "Testing login success failed, Expected: response.status = True")

        # channel.close()

    def test_login_failure(self): # Failure login case
        # channel = Channel(host="127.0.0.1", port=50051)
        # service = AccountPackage.AccountServiceStub(channel)
        
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.try_login(username="FalseCredentialUsername", password="FalseCredentialPassword"))

        print(response)
        self.assertFalse(response.status, "Testing login failure failed, Expected: response.status = False")

        # channel.close()

# Testing register_user, should also add roles to this
class TestRegisterUser(unittest.TestCase):
    def test_register_invalid_password(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(2001,2,1), email="email", password="pa", business_area_id=1))

        print(response)
        self.assertFalse(response.status, "Testing invalid password registration, Expected: response.status = False")

    def test_register_invalid_name(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="", date_of_birth=datetime.datetime(2001,2,1), email="email", password="password", business_area_id=1))

        print(response)
        self.assertFalse(response.status, "Testing invalid name registration, Expected: response.status = False")

    def test_register_invalid_dob(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(3000,2,1), email="email", password="password", business_area_id=1))

        print(response)
        self.assertFalse(response.status, "Testing invalid dob registration, Expected: response.status = False")

    def test_register_invalid_email(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(2001,2,1), email="", password="password", business_area_id=1))

        print(response)
        self.assertFalse(response.status, "Testing invalid email registration, Expected: response.status = False")

    def test_register_invalid_password(self):
        # loop = asyncio.get_event_loop_policy().get_event_loop()
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(2001,2,1), email="email", password="password", business_area_id=-1))

        print(response)
        self.assertFalse(response.status, "Testing invalid business area id registration, Expected: response.status = False")

    # Test pre-existing registration
    def test_preexisting_registration(self):
        response = loop.run_until_complete(service.register_user(name="name", date_of_birth=datetime.datetime(2001,2,1), email="test@gmail.com", password="password", business_area_id=1))

        print(response)
        self.assertFalse(response.status, "Testing registration for pre-existing user, Expected: response.status = False")

    def test_register_success(self):
        randomstring = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 10))
        print(randomstring)
        randomemail = randomstring + "@gmail.com"
        print(randomemail)
        response = loop.run_until_complete(service.register_user(name="testname", date_of_birth=datetime.datetime(2001,2,1), email=randomemail, password="password", business_area_id=1))

        print(response)
        self.assertTrue(response.status, "Testing registration of valid user w/ randomly generated email, Expected: response.status = True")
        # Either need to delete original user from database or generate some random client

class TestAccountProfiles(unittest.TestCase):
    def test_is_mentor_true(self):
        response = loop.run_until_complete(service.account_profiles(userid=20))

        print(response)
        self.assertTrue(response.is_mentor, "Testing account profile userid = 20, Expected: response.is_mentor = True")
        # self.assertFalse(response.is_mentee, "Testing account profile userid = 20, Expected: response.is_mentee = False")

    def test_is_mentee_true(self):
        response = loop.run_until_complete(service.account_profiles(userid=41))

        print(response)
        self.assertTrue(response.is_mentee, "Testing account profile userid = 41, Expected: response.is_mentee = True")
        # self.assertFalse(response.is_mentor, "Testing account profile userid = 41, Expected: response.is_mentor = False")

    def test_is_mentor_failure(self):
        response = loop.run_until_complete(service.account_profiles(userid=56))

        print(response)
        self.assertFalse(response.is_mentor, "Testing account profile userid = 56, Expected: response.is_mentor = False")

    def test_is_mentee_failure(self):
        response = loop.run_until_complete(service.account_profiles(userid=4))

        print(response)
        self.assertFalse(response.is_mentee, "Testing account profile userid = 4, Expected: response.is_mentee = False")

class TestListBusinessAreas(unittest.TestCase):
    def test_list_business_areas(self):
        response = loop.run_until_complete(service.list_business_areas())

        print(response)
        self.assertEqual(response.business_areas, [AccountPackage.BusinessArea(id=1, name='Private Bank'), AccountPackage.BusinessArea(id=2, name='Corporate Bank'), AccountPackage.BusinessArea(id=3, name='Asset Management'), AccountPackage.BusinessArea(id=4, name='Investment Bank')], "Testing business areas function, Expected: response.business_areas = [BusinessArea(id=1, name='Private Bank'), BusinessArea(id=2, name='Corporate Bank'), BusinessArea(id=3, name='Asset Management'), BusinessArea(id=4, name='Investment Bank')]")

class TestSkillsListing(unittest.TestCase):
    def test_skills_listing(self):
        response = loop.run_until_complete(service.list_skills())

        print(response)
        self.assertEqual(response.skills,[AccountPackage.Skill(id=1, name='Technical'),    AccountPackage.Skill(id=2, name='How To Progress Career'), AccountPackage.Skill(id=3, name='Management'), AccountPackage.Skill(id=4, name='Leadership'), AccountPackage.Skill(id=5, name='Healthy Work-Life balance')] , "Testing list skills function, Expeted: response.skills = [Skill(id=1, name='Technical'), Skill(id=2, name='How To Progress Career'), Skill(id=3, name='Management'), Skill(id=4, name='Leadership'), Skill(id=5, name='Healthy Work-Life balance')]")

class TestNotifications(unittest.TestCase): # Ask about this test
    def test_notis(self):
        response = loop.run_until_complete(service.get_notifications(userid=41, target_profile_type=0))

        print(response)
        self.assertEqual(response.desired_notifications, ['Message to mentee_1: Resource put white beyond great summer speak. Surface month interview move history. Material already church.\r\nReflect set sound measure per a. Contain rise miss between sort list set.'], "Testing notification retrieval, Expected: Notification")

    # def test_empty_notis(self):
    #     response = loop.run_until_complete(service.get_notifications(userid=20, target_profile_type=1))

    #     print(response)
    #     self.assertEqual(response, AccountPackage.NotificationsReply(), "Testing empty notification set, Expected empty NotificationsReply()")

class TestRegisterRoles(unittest.TestCase):
    def test_register_mentor(self):
        randomstring = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 10))
        print(randomstring)
        randomemail = randomstring + "@gmail.com"
        print(randomemail)
        response1 = loop.run_until_complete(service.register_user(name="testname", date_of_birth=datetime.datetime(2001,2,1), email=randomemail, password="password", business_area_id=1))
        uid = response1.account_id
        print(response1)

        response2 = loop.run_until_complete(service.register_mentor(userid=response1.account_id, desired_skills=[]))

        print(response2)

        response3 = loop.run_until_complete(service.account_profiles(userid=uid))
        self.assertTrue(response3.is_mentor, "Testing mentor registration, Expected: response3.is_mentor = True")

    def test_register_mentee(self):
        randomstring = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 10))
        print(randomstring)
        randomemail = randomstring + "@gmail.com"
        print(randomemail)
        response1 = loop.run_until_complete(service.register_user(name="testname", date_of_birth=datetime.datetime(2001,2,1), email=randomemail, password="password", business_area_id=1))
        uid = response1.account_id
        print(response1)

        response2 = loop.run_until_complete(service.register_mentee(userid=response1.account_id, desired_skills=[]))

        print(response2)

        response3 = loop.run_until_complete(service.account_profiles(userid=uid))
        self.assertTrue(response3.is_mentee, "Testing mentee registration, Expected: response3.is_mentee = True")


# Tests runs on same channel connections
channel = Channel(host="127.0.0.1", port=50051)
service = AccountPackage.AccountServiceStub(channel)
loop = asyncio.get_event_loop_policy().get_event_loop()


if __name__  == '__main__':
    unittest.main()
    
channel.close()