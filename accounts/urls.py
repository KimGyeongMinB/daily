from django.urls import path, include

from .views import SignupAPIView, SignupVerifyAPIView, CustomTokenObtainPairView, CustomTokenRefreshView, CustomTokenBlacklistView, KakaoLogin, KakaoLoginStartView, KakaoCallbackView

app_name = "accounts"

urlpatterns = [
    path('sign-up/', SignupAPIView.as_view(), name="sign_up"), # 회원가입 이메일 인증
    path('verfiy-code/', SignupVerifyAPIView.as_view(), name="sign_up_verify"), # 회원가입 완료
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), # 로그인
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'), # 토큰 리프레시
    
    # 사용자가 브라우저에 입력할 주소
    path('auth/kakao/start/', KakaoLoginStartView.as_view(), name='kakao_start'),
    
    # 카카오가 돌아올 주소 (인가 코드가 화면에 보임)
    path('kakao/callback/', KakaoCallbackView.as_view(), name='kakao_callback'),
    
    # 스웨거에서 POST로 실제 로그인할 주소
    path('auth/kakao/login/', KakaoLogin.as_view(), name='kakao_login_post'),
    
    
    path('api/token/blacklist/', CustomTokenBlacklistView.as_view(), name='token_blacklist'), # 로그아웃
]