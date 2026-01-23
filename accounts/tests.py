from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

class SignupTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.nickname = "testnickname"
        self.email = "test123@test.com"
        self.password = "test12345"
        self.signup_url = reverse("accounts:sign_up")

    def testsignup(self):
        sign_up = self.client.post(
            path=self.signup_url,
            data={
                "nickname": self.nickname,
                "email": self.email,
                "password": self.password
            },
            format="json"
            )
        
        self.assertEqual(sign_up.status_code, status.HTTP_201_CREATED)