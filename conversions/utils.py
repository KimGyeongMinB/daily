from .models import ConversionLog

class ConversionLogUtils:
    @staticmethod
    def conversion_log(conversion, status, retry_count=0, error_code="", 
                    error_message="",task_id="", extra=None,):
        """
        conversion log 함수
        """

        if extra is None:
            extra = {}

        return ConversionLog.objects.create(
            conversion=conversion,
            status=status,
            retry_count=retry_count,
            error_code=error_code,
            error_message=error_message,
            task_id=task_id,
            extra=extra,
            )
