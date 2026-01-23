from rest_framework import serializers
from django.contrib.auth import get_user_model


# 회원가입 전용
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