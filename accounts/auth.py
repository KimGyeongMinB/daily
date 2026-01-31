from rest_framework.request import Request

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

# 인증
class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request: Request):
        header = request.COOKIES.get("access_token")
        if header is None:
            return None
        
        validated_token = self.get_validated_token(header)
        user = self.get_user(validated_token)

        if not validated_token:
            raise InvalidToken("유효하지 않은 토큰입니다.")
        
        if not user:
            raise AuthenticationFailed("해당 토큰에 대한 사용자를 찾을 수 없습니다.")
        
        return (user, validated_token)