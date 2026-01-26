from typing import Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer, TokenRefreshSerializer)
from rest_framework_simplejwt.tokens import RefreshToken

# 회원가입
class SignupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = get_user_model() # User Model
        fields = ("nickname", "email", "password")

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
