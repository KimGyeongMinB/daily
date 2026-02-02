from django.core.cache import cache
from django.contrib.auth import get_user_model

# swagger
from drf_spectacular.utils import extend_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# jwt
from rest_framework_simplejwt.views import (TokenObtainPairView, 
TokenRefreshView, TokenBlacklistView)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

# serializer
from .serializers import (SignupSerializer, SignupVerifySerializer,
                        CustomTokenObtainPairSerializer, CustomTokenBlacklistSerializer)

from .utils import sendemailrandomcodehelper

# 트랜잭션
from django.db import transaction

# task
from .tasks import send_verification_email


User = get_user_model()

class SignupAPIView(APIView):
    @extend_schema(
    summary="회원가입 이메일 발송 API",
    description="이메일 입력후 celery 를 통해 해당 이메일에 코드 발송, 발송에 성공할시 캐시에 이메일과, 코드가 5분동안 저장됩니다",
    request=SignupSerializer,
    responses={200: SignupSerializer})
    
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            code = sendemailrandomcodehelper.make_random_code()
            cache.set(key=f"signup_data:{serializer.validated_data["email"]}",
                    value={
                        "email": serializer.validated_data["email"],
                        "code": code,
                    },
                    timeout=300 # 5분
                    )
            
            send_verification_email.delay(serializer.validated_data["email"], code)
            return Response({"message": "전송완료"}, status.HTTP_200_OK)

class SignupVerifyAPIView(APIView):
    @extend_schema(
    summary="회원가입 이메일 인증 API",
    description=(
        "이메일에서 발급받은 코드, 해당 이메일, 닉네임, 패스워드를 입력하면 인증이 완료됩니다.\n" 
        "중복된 이메일일 경우 캐시가 삭제 됩니다.\n"
        "실패시 트랜잭션에 의해 회원가입이 취소됩니다."
        ),
    request=SignupVerifySerializer,
    responses={200: SignupVerifySerializer})

    def post(self, request):
        serializer = SignupVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        # 중복된 이메일일 경우 캐시 삭제
        if User.objects.filter(email=email).exists():
            cache.delete(f"signup_data:{email}")
            return Response({"message": "이미 가입 처리된 이메일입니다."},
                                status=status.HTTP_200_OK)

        # 트랜잭션 적용
        with transaction.atomic():
            serializer.save()
            cache.delete(f"signup_data:{email}")
        return Response({"message": "유저 생성이 완료 되었습니다."}, status=200)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
    summary="JWT 로그인 커스텀",
    description=(
        "사용자 이메일과 패스워드를 입력받아 토큰을 발급받아 쿠키에 저장합니다.\n"
        "보안 강화를 위해 다음 설정이 적용되어 있습니다.\n"
        "1) XSS 공격 방지를 위한 httponly=True 설정\n"
        "2) CSRF 공격 방지 및 완화를 위한 samesite='Lax' 설정\n"
        "3) 데이터 암호화 전송을 위한 secure=True(운영 환경), 현재는 개발환경임으로 False 설정\n"
        "4) 보안을 위해 응답 본문(JSON)에서 토큰을 제거하고 전송 과정에서 토큰 노출을 최소화했습니다."
    ),
    request=CustomTokenObtainPairSerializer,
    responses={200: CustomTokenObtainPairSerializer})

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access_token = response.data.get('access')
        refresh_token = response.data.get('refresh')

        # access_token
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True, # 자바스크립트 접근 불가능(XSS 방지)
            secure=False, # https 에서만 연결(개발시 False)
            samesite='Lax' # CSRF 완화
        )

        # refresh_token
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True, # 자바스크립트 접근 불가능(XSS 방지)
            secure=False, # https 에서만 연결(개발시 False)
            samesite='Lax' # CSRF 완화
        )

        # json 데이터 삭제
        del response.data['access']
        del response.data['refresh']

        return response

class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(
        summary="Access 토큰 갱신",
        description=(
            "쿠키에 저장된 `refresh_token`을 사용하여 새로운 `access_token`을 발급하고 쿠키를 갱신합니다.\n"
            "1) XSS 공격 방지를 위한 httponly=True 설정\n"
            "2) CSRF 공격 방지 및 완화를 위한 samesite='Lax' 설정\n"
            "3) 데이터 암호화 전송을 위한 secure=True(운영 환경), 현재는 개발환경임으로 False 설정\n"
            "4) 보안을 위해 응답 본문(JSON)에서 토큰을 제거하여 클라이언트 노출을 차단했습니다."
        ),
        request=None,
        responses={200: None}
    )

    def post(self, request, *args, **kwargs):
        # 쿠키에서 리프레시 토큰 가져오기
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "리프레시 토큰이 없습니다."}, status=401)
        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        access_token = response.data.get("access")
        refresh_token = response.data.get("refresh")
        
        # access_token
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True, # 자바스크립트 접근 불가능(XSS 방지)
            secure=False, # https 에서만 연결(개발시 False)
            samesite='Lax' # CSRF 완화
        )

        # refresh_token
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True, # 자바스크립트 접근 불가능(XSS 방지)
            secure=False, # https 에서만 연결(개발시 False)
            samesite='Lax' # CSRF 완화
        )

        # json 데이터 삭제
        del response.data['access']
        del response.data['refresh']

        return response

class CustomTokenBlacklistView(TokenBlacklistView):
    serializer_class = CustomTokenBlacklistSerializer
    @extend_schema(
        summary="로그 아웃 및 토큰 블랙리스트",
        description=(
            "쿠키에 저장된 `refresh_token`을 무효화(Blacklist) 처리하고, 브라우저의 인증 쿠키를 삭제합니다.\n"
            "1) **토큰 무효화**: 사용된 리프레시 토큰을 블랙리스트에 등록하여 재사용을 차단합니다.\n"
            "2) **쿠키 제거**: 브라우저에 저장된 `access_token`과 `refresh_token` 쿠키를 즉시 삭제합니다.\n"
            "3) **클라이언트 보안**: 서버 응답에서 토큰 정보를 완전히 제외하여 보안성을 높였습니다.\n"
            "4) **자동 인증 해제**: 이후 요청부터는 유효한 토큰이 없으므로 인증되지 않은 사용자로 처리됩니다."
        ),
        request=None,
        responses={200: None}
    )

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get("refresh_token")
        print(refresh)
        serializer = self.get_serializer(data={"refresh": refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        response = Response({"detail": "로그아웃 완료"}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token")
        return response