from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
# swagger
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from .models import Conversion
from .serializers import ConversionSerializer

import requests
import os

load_dotenv() # 환경변수 읽어오기
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

# openai
class ConversionAPIView(APIView):
    @extend_schema(
        summary="글 변환(쉬운 글로 변환) API",
        description=(
            "입력된 텍스트나 URL의 본문 내용을 분석하여 경계선 지능인을 위한 쉬운 글로 변환합니다.\n\n"
            "[동작 방식]\n"
            "1. 텍스트 우선: `text`가 입력되면 해당 내용을 우선적으로 변환합니다.\n"
            "2. URL 크롤링: `text`가 없고 `url`만 있다면 해당 주소의 본문을 크롤링하여 사용합니다.\n"
            "3. AI 변환: GPT-4o-mini 모델을 사용하여 어려운 단어(한자, 영어) 풀이와 4줄 이내 요약을 수행합니다.\n\n"
            "[주의 사항]\n"
            "외부 사이트 크롤링 및 AI 응답 대기로 인해 응답 시간이 수 초 정도 소요될 수 있습니다."
        ),
        request=ConversionSerializer,
        responses={
            201: ConversionSerializer,
            200: OpenApiTypes.OBJECT, # 실패 시에도 상태값 반환을 위해 명시
        }
    )
    
    def post(self, request):
        serializer = ConversionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 시리얼라이저에서 가져온 데이터로 생성
        # 트랜잭션 적용
        with transaction.atomic():
            conversion = Conversion.objects.create(
                author=request.user,
                text=serializer.validated_data.get("text"),
                url=serializer.validated_data.get("url"),
            )

        # 저장된 데이터
        # url 만 있는 경우 url 로 들어가서 본문 내용 가져오기와 input_text에 넣기
        input_text = conversion.text
        input_url = conversion.url
        if not input_text and input_url:
            try:
                headers = {'User-Agent' : 'Mozilla/5.0'}
                resp = requests.get(input_url, headers=headers, timeout=5)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser') # 본문가져오기
                input_text = soup.get_text(separator=' ')

            except Exception as e:
                return Response({"상태": conversion.status, "결과": conversion.result}, status=status.HTTP_200_OK)

        try:
            # "gpt-4o-mini" 불러오기
            conversion.status_processing() # status 진행중으로 변경 모델메서드
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {'role': 'system', "content": ("너는 경계선 지능인을 위해 어려운 글을 이해하기 쉬운 글로 만들어 주는 도우미, 모르는 말(영어, 한자 등등)이 있으면 뜻을 함께 써줘. 바꾼 글만 보여주고 바뀐글은 4줄 이내로 정리. 문장은 짧게 써.")},
                    {'role':'user','content': input_text}
                ]
            )
            # 성공
            conversion.status_done(completion.choices[0].message.content)
            return Response(ConversionSerializer(conversion).data, status=status.HTTP_201_CREATED)
        
        # 실패
        except Exception as e:
            conversion.status_fail()
            print(f"!!! 에러 발생 원인: {e}")
            return Response({"상태": conversion.status, "결과": conversion.result}, status=status.HTTP_200_OK)