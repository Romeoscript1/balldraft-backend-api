from rest_framework.test import APITestCase
from django.urls import reverse

class TestCaseSetUp(APITestCase):
    '''Test setup for all test'''

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')

        self.user_data = {
            "email":"test@user.com",
            "first_name":"test",
            "last_name":"user",
            "dob":"2000-02-13",
            "password":"Test1234.",
            "password2":"Test1234."
        }

        return  super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()