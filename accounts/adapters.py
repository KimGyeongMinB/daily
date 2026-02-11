from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .utils import RandomNickname

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        # 기본 저장 로직 실행
        user = super().save_user(request, sociallogin, form)
        
        user.nickname = RandomNickname.make_random_nickname() 
        user.save()
        return user