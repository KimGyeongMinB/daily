import string
import secrets
import random
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

class SendEmailRandomCodeHelper:
    """
    코드 6자리 랜덤으로 만들어주는 클래스
    """
    def make_random_code(self):
        random_code = string.ascii_letters + string.digits
        return "".join(secrets.choice(random_code) for _ in range(6))

sendemailrandomcodehelper = SendEmailRandomCodeHelper()

class RandomNickname:
    """
    코드 6자리 랜덤으로 만들어주는 클래스
    """
    def make_random_nickname(self):
        adjectives = ["행복한", "즐거운", "용감한", "빠른", '멍청한', '느린', '키가 큰']
        animals = ["사자", "고래", "다람쥐", "독수리", '고양이', '달팽이', '기린']
        num = random.randint(1000, 9999)
        return f"{random.choice(adjectives)}{random.choice(animals)}{num}"

class SetCookie:
    """
    로그인 토큰 (access/refresh) 쿠키에 저장
    """  
    def response_set_cookie(response, access_token, refresh_token):
        try:
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True, # 자바스크립트 접근 불가능(XSS 방지)
                secure=False, # https 에서만 연결(개발시 False)
                samesite='Lax' # CSRF 완화
            )

            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True, # 자바스크립트 접근 불가능(XSS 방지)
                secure=False, # https 에서만 연결(개발시 False)
                samesite='Lax' # CSRF 완화
            )

            del response.data['access']
            del response.data['refresh']
            return response
        
        except Exception as e:
            raise Exception(f"로그인 토큰 처리 과정중 문제 발생: {str(e)}")

class Kakaoauth:
    """
    카카오로그인 유틸 클래스
    """
    def kakao_auth_url(self):
        client_id = os.getenv("CLIENT_ID")
        if not client_id:
            raise ValueError("CLIENT_ID 환경 변수가 설정되지 않았습니다.")
        
        response_type = 'code'
        state = str(uuid.uuid4())

        redirect_uri = "http://localhost:8000/accounts/kakao/callback"
        if not redirect_uri:
                raise ValueError("redirect_uri가 설정되지 않았습니다.")

        try:
            kakao_auth_url = ( 
                f"https://kauth.kakao.com/oauth/authorize?" 
                f"client_id={client_id}&redirect_uri={redirect_uri}"
                f"&response_type={response_type}&state={state}" 
                )
            return kakao_auth_url
        
        except Exception as e:
            raise Exception(f"카카오 인증 URL 생성 중 오류 발생: {str(e)}")
