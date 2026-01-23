from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import SignupAPIView

app_name = "accounts"

urlpatterns = [
    path('sign-up/', SignupAPIView.as_view(), name="sign_up"), # 회원가입
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]