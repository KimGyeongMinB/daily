from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.db import transaction
from django.test import TransactionTestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase, override_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class TransactionTests(TransactionTestCase):
    """
    트랜잭션 테스트
    """
    def test_transaction(self):
        with self.assertRaises(Exception):
            with transaction.atomic():
                User.objects.create_user(
                email="test@example.com",
                password="password123!",
                nickname="testboy")
                raise Exception("중간 에러 발생") 
        self.assertEqual(User.objects.count(), 0)

class SignupTests(APITestCase):    
    """
    회원가입 테스트
    """
    def setUp(self):
        self.client = APIClient()
        self.email = "test123@test.com"
        self.nickname = "testuser"
        self.password = "test1234@@"
        self.exists_email = "test123@test.com" # 이미 존재하는 이메일 검증
        self.code = "123456"
        self.signup_url = reverse("accounts:sign_up")
        self.signup_verify_url = reverse("accounts:sign_up_verify")

    # 테스트 이메일 발송
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def testsignup_email(self):
        sign_up = self.client.post(
            path=self.signup_url,
            data={
                "email": self.email,
            },
            format="json"
            )
        # 캐시 저장
        cache.set(key=f"signup_data:{self.email}", value={"email": self.email,"code": self.code})

        # 확인
        self.assertEqual(sign_up.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    # 테스트 이메일 인증
    def testsignup_verify(self):
        verify_code = cache.get(f"signup_data:{self.email}")
        self.assertIsNotNone(verify_code)
        code = verify_code.get("code")

        sign_up_verify = self.client.post(
            path=self.signup_verify_url,
            data={
                "email": self.email,
                "nickname": self.nickname,
                "password": self.password,
                "code": code

            },
            format="json"
            )
        
        # 캐시 삭제
        cache.delete(f"signup_data:{self.email}")

        # 확인
        self.assertEqual(sign_up_verify.status_code, status.HTTP_200_OK)

    # 메일이 이미 가입되어 있는 경우
    def testsignup_exists_email(self):
        User.objects.create_user(
            email=self.email,
            nickname=self.nickname,
            password=self.password,
        )

        sign_up = self.client.post(
            path=self.signup_url,
            data={
                "email": self.exists_email,
            },
            format="json"
            )
        
        # 확인
        self.assertEqual(sign_up.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("이미 가입된 이메일입니다.", sign_up.data)

class SigninTests(APITestCase):
    """
    로그인 테스트
    """
    def setUp(self):
        self.client = APIClient()
        self.nickname = "testnickname"
        self.email = "test123@test.com"
        self.password = "test12345"
        self.signin_url = reverse("accounts:token_obtain_pair")

    # 테스트 로그인
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

        # 토큰값이 들어있는지 확인
        self.assertIn('access_token', sign_in.cookies)
        self.assertIn('refresh_token', sign_in.cookies)


class LogoutTest(APITestCase):
    """
    로그아웃 테스트
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123!",
            nickname="testboy"
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)
        self.logout_url = reverse("accounts:token_blaclist")

    # 로그아웃 테스트
    def testlogout(self):
        self.client.cookies['refresh_token'] = self.refresh_token
        response = self.client.post(self.logout_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies.get("refresh_token").value, "")
        self.assertEqual(response.cookies.get("access_token").value, "")

        blacklist = BlacklistedToken.objects.filter(token__token=self.refresh_token).exists()
        self.assertTrue(blacklist, "토큰이 블랙리스트에 등록되어야 합니다.")
