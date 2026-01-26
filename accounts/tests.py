from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


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

class SigninTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.nickname = "testnickname"
        self.email = "test123@test.com"
        self.password = "test12345"
        self.signin_url = reverse("accounts:token_obtain_pair")

    def testsignin(self):
        User.objects.create_user(
            nickname = self.nickname,
            email = self.email,
            password = self.password
        )

        sign_in = self.client.post(
        path=self.signin_url,
            data={
                "email": self.email,
                "password": self.password
            },
            format="json"
            )
        
        self.assertEqual(sign_in.status_code, status.HTTP_200_OK)