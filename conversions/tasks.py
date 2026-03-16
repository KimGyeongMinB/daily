import requests
import os

from celery import shared_task, chain
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

from .models import Conversion
from .utils import ConversionLogUtils

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))


@shared_task
def request_text_beautifulsoup_task(input_url, timeout: int):
    # URL 본문을 가져와서 HTML 태그를 제거한 순수 텍스트로 반환
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(input_url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    return soup.get_text(separator=' ')


@shared_task
def openai_task(input_text, conversion_id):
    # 현재 변환 작업 객체 조회
    conversion = Conversion.objects.get(id=conversion_id)

    # AI 처리 시작 상태로 변경
    conversion.status_processing()

    # OpenAI에 텍스트를 보내 쉬운 문장으로 변환
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                'role': 'system',
                "content": (
                    "너는 경계선 지능인을 위해 어려운 글을 이해하기 쉬운 글로 만들어 주는 도우미다.\n"
                    "모르는 말(영어, 한자 등)이 있으면 뜻을 함께 써라.\n"
                    "바꾼 글만 보여주고 4줄 이내로 정리하라.\n"
                    "문장은 짧게 써라."
                )
            },
            {'role': 'user', 'content': input_text}
        ]
    )

    # 응답 결과를 저장하고 상태를 완료로 변경
    result_text = completion.choices[0].message.content
    conversion.status_done(result_text)

    return {"conversion_id": conversion_id}


@shared_task(bind=True, max_retries=2)
def run_openai_task(self, conversion_id):
    # 변환 작업 조회
    conversion = Conversion.objects.get(id=conversion_id)

    # task 시작 시점 로그 저장
    ConversionLogUtils.conversion_log(
        conversion=conversion,
        status="PROCESSING",
        retry_count=self.request.retries,
        task_id=self.request.id,
        extra={"source": "task_start"},
    )

    input_text = conversion.text
    input_url = conversion.url

    try:
        # text가 있으면 바로 OpenAI task만 실행
        if input_text:
            task = chain(
                openai_task.s(input_text, conversion_id)
            )

        # text가 없고 url만 있으면
        # 1. URL 본문 추출
        # 2. 추출된 본문을 OpenAI에 전달
        else:
            task = chain(
                request_text_beautifulsoup_task.s(input_url, timeout=5),
                openai_task.s(conversion_id)
        )
    
        ConversionLogUtils.conversion_log(
            conversion=conversion,
            status="DONE",
            retry_count=self.request.retries,
            task_id=self.request.id,
            extra={"source": "task_done"},
        )

    # 예외처리
    except Exception as e:
        ConversionLogUtils.conversion_log(
            conversion=conversion,
            status="FAILED",
            retry_count=self.request.retries,
            error_code=e.__class__.__name__,
            error_message=str(e),
            task_id=self.request.id,
            extra={"source": "task_error"},
        )
        conversion.status_fail()

    # 실제 Celery 비동기 작업 실행
    task.apply_async()

    # 바로 응답용 데이터만 반환
    return {"conversion_id": conversion_id}
