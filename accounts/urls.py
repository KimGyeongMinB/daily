from django.urls import path

from .views import SignupAPIView, SignupVerifyAPIView, CustomTokenObtainPairView, TestJWT, CustomTokenRefreshView, CustomTokenBlacklistView

app_name = "accounts"

urlpatterns = [
    path('sign-up/', SignupAPIView.as_view(), name="sign_up"), # 회원가입
    path('verfiy-code/', SignupVerifyAPIView.as_view(), name="sign_up_verify"), # 회원가입
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('test/', TestJWT.as_view()),
    path('api/token/blacklist/', CustomTokenBlacklistView.as_view(), name='token_blaclist'),
]