from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from conversions.models import Conversion


User = get_user_model()


class ConversionModelMethodTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="Test1234!!",
            nickname="test1234"
        )

        self.conversion = Conversion.objects.create(
            author=self.user,
            text="원문 텍스트",
            url="https://example.com",
            result="",
            status="PENDING"
        )

    def test_status_processing_updates_only_status(self):
        self.conversion.status_processing()
        self.conversion.refresh_from_db()

        self.assertEqual(self.conversion.status, "PROCESSING")
        self.assertEqual(self.conversion.result, "")

    def test_status_fail_updates_status_and_result(self):
        self.conversion.status_fail()
        self.conversion.refresh_from_db()

        self.assertEqual(self.conversion.status, "FAILED")
        self.assertEqual(
            self.conversion.result,
            "URL에서 글을 가져오지 못했습니다. 글 내용을 복사해서 text로 붙여넣어 주세요."
        )

    def test_status_done_updates_status_and_result(self):
        result_text = "변환 완료 결과입니다."

        self.conversion.status_done(result_text)
        self.conversion.refresh_from_db()

        self.assertEqual(self.conversion.status, "DONE")
        self.assertEqual(self.conversion.result, result_text)
