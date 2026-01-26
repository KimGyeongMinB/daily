from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# jwt
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# serializer
from .serializers import SignupSerializer, CustomTokenObtainPairSerializer

# 회원가입
class SignupAPIView(APIView):
    
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 로그인 커스텀
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

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

# 리프레시 토큰 발급
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # 쿠키에서 리프레시 토큰 가져오기
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "리프레시 토큰이 없습니다."}, status=401)
        
        request.data["refresh_token"] = refresh_token
        response = super().post(request, *args, **kwargs)
        access_token = response.data.get("access")
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



class TestJWT(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"ok": True})
