from django.urls import path

from .views import SignupAPIView, CustomTokenObtainPairView, TestJWT, CustomTokenRefreshView

app_name = "accounts"

urlpatterns = [
    path('sign-up/', SignupAPIView.as_view(), name="sign_up"), # 회원가입
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('test/', TestJWT.as_view())
]