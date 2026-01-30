import string
import secrets

class SendEmailRandomCodeHelper:
    def make_random_code(self):
        random_code = string.ascii_letters + string.digits
        return "".join(secrets.choice(random_code) for _ in range(6))

sendemailrandomcodehelper = SendEmailRandomCodeHelper()