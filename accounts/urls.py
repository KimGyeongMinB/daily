from django.urls import path
from .views import SignupAPIView

app_name = "accounts"

urlpatterns = [
    path('sign-up/', SignupAPIView.as_view(), name="sign_up") # 회원가입
]