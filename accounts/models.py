from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# 유저 생성 매니저
class UserManager(BaseUserManager):
    def create_user(self, email, password=None,  nickname=None, **extra_fields):
        if not email:
            raise ValueError("이메일을 입력해주세요.")
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)

        # 비밀번호 해시
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    # 입력해야하는 필드
    nickname = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    # 비 입력 필드
    date_join = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 로그인 시 이름 대신 이메일로 인증
    # 슈퍼계정 만들때 닉네임 추가로 받음
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    # 유저 매니저 클래스 연결
    objects = UserManager()

    class Meta:
        db_table = 'users'
    
    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active"])
    
    def active(self):
        self.is_active = True
        self.save(update_fields=["is_active"])