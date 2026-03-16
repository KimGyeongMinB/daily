from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction

# swagger
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from openai import OpenAI
from dotenv import load_dotenv

from .utils import ConversionLogUtils
from .tasks import run_openai_task

# from bs4 import BeautifulSoup

from .models import Conversion
from .serializers import ConversionSerializer

# import requests
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

        ConversionLogUtils.conversion_log(
            conversion=conversion,
            status="PENDING",
            extra={
                "source": "view",
                "text": bool(conversion.text),
                "url": bool(conversion.url)
            }
        )

        run_openai_task.delay(conversion.id)
        return Response(
            {"conversion_id": conversion.id, "status": conversion.status},
            status=status.HTTP_201_CREATED
        )
    
    def get(self, request, conversion_id):
        conversion = Conversion.objects.get(id=conversion_id)
        return Response(ConversionSerializer(conversion).data, status=200)