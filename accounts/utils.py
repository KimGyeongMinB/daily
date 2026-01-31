import string
import secrets

# 코드 6자리 랜덤으로 만들어주는 클래스
class SendEmailRandomCodeHelper:
    def make_random_code(self):
        random_code = string.ascii_letters + string.digits
        return "".join(secrets.choice(random_code) for _ in range(6))

sendemailrandomcodehelper = SendEmailRandomCodeHelper()