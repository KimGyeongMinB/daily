from django.db import models
from django.contrib.auth import get_user_model

# 유저 모델
User = get_user_model()

class Conversion(models.Model):
    # 작성자, 글, URL, 결과, 작성시간

    STATUS_CHOICES = [
        ("PENDING", "대기"),
        ("PROCESSING", "처리중"),
        ("DONE", "완료"),
        ("FAILED", "실패"),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversion")
    text = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    result = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def status_fail(self):
        self.status = "FAILED"
        self.result = "URL에서 글을 가져오지 못했습니다. 글 내용을 복사해서 text로 붙여넣어 주세요."
        self.save(update_fields=["status", "result"])

    def status_processing(self):
        self.status = "PROCESSING"
        self.save(update_fields=["status"])

    def status_done(self, result_text):
        self.status = "DONE"
        self.result = result_text
        self.save(update_fields=["status", "result"])