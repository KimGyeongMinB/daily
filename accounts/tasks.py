from django.contrib.auth import get_user_model
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

User = get_user_model()

# 이메일 인증
@shared_task
def send_verification_email(email, code):
    send_mail(
        subject = "이메일 인증 코드입니다",
        message = f"인증 코드는 {code} 입니다.",
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [email]
    )