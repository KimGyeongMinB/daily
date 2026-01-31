from rest_framework import serializers
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer, 
                                                TokenBlacklistSerializer)

from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()

# 회원가입
class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        # 이미 가입된 이메일인지
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
        return value
    
    def signup_payload(self):
        # 캐시 저장 데이터 페이로드
        data = {
            "email": self.validated_data["email"]
        }
        return data

# 회원가입 코드 입력, 이메일, 닉네임, 패스워드 입력하는 시리얼라이저
class SignupVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)
    email = serializers.EmailField()
    nickname = serializers.CharField(min_length=3)
    password = serializers.CharField(min_length=6)

    def validate(self, attrs):
        email = attrs["email"]
        code = attrs["code"]

        saved_cache = cache.get(f"signup_data:{email}")

        if not saved_cache:
            raise serializers.ValidationError("인증 정보가 없거나 만료되었습니다. 다시 요청해주세요.")
        
        saved_cache_code = saved_cache.get("code")

        if code != saved_cache_code:
            raise serializers.ValidationError("인증 코드가 올바르지 않습니다.")
        
        attrs["signup_data"] = saved_cache
        return attrs

    # 유저 회원가입 생성 함수
    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            nickname=validated_data['nickname'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user

# 로그인
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    # 토큰 추출
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token["user_id"] = user.id
        return token
    
    # json 응답용
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": getattr(self.user, "email", ""),
            "nickname": getattr(self.user, "nickname", ""),
        }

        return data

class CustomTokenBlacklistSerializer(TokenBlacklistSerializer):
    pass