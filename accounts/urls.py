from django.urls import path

from .views import SignupAPIView, SignupVerifyAPIView, CustomTokenObtainPairView, CustomTokenRefreshView, CustomTokenBlacklistView

app_name = "accounts"

urlpatterns = [
    path('sign-up/', SignupAPIView.as_view(), name="sign_up"), # 회원가입 이메일 인증
    path('verfiy-code/', SignupVerifyAPIView.as_view(), name="sign_up_verify"), # 회원가입 완료
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), # 로그인
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'), # 토큰 리프레시
    path('api/token/blacklist/', CustomTokenBlacklistView.as_view(), name='token_blaclist'), # 로그아웃
]