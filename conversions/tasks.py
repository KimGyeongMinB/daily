import requests
import os

from celery import shared_task, chain

from bs4 import BeautifulSoup

from openai import OpenAI

from dotenv import load_dotenv

from .serializers import ConversionSerializer
from .models import Conversion

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

@shared_task
def request_text_beautifulsoup_task(input_url, timeout: int):
    headers = {'User-Agent' : 'Mozilla/5.0'}
    resp = requests.get(input_url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    return soup.get_text(separator=' ')

@shared_task
def openai_task(input_text, conversion_id):
    conversion = Conversion.objects.get(id=conversion_id)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {'role': 'system', "content": ("너는 경계선 지능인을 위해 어려운 글을 이해하기 쉬운 글로 만들어 주는 도우미, 모르는 말(영어, 한자 등등)이 있으면 뜻을 함께 써줘. 바꾼 글만 보여주고 바뀐글은 4줄 이내로 정리. 문장은 짧게 써.")},
            {'role':'user','content': input_text}
        ]
    )
    result_text = completion.choices[0].message.content
    conversion.status_done(result_text)

    return {"conversion_id": conversion_id}

@shared_task(bind=True, max_retries=2)
def run_openai_task(self, conversion_id):
    conversion = Conversion.objects.get(id=conversion_id)
    conversion.status_processing()
    input_text = conversion.text
    input_url = conversion.url

    if input_text:
        task = chain(
            openai_task.s(input_text)
        )

    else:
        task = chain(
            request_text_beautifulsoup_task.s(input_url, timeout=5),
            openai_task.s(conversion_id)
        )

    task.apply_async()
    return {"conversion_id": conversion_id}