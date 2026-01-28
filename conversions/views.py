from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ConversionSerializer
from django.db import transaction
from .models import Conversion
import openai
import requests
from dotenv import load_dotenv
import os

load_dotenv() # 환경변수 읽어오기

openai_key = os.getenv("OPEN_API_KEY")

class ConversionAPIView(APIView):

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
                resp = requests.get(input_url, timeout=5)
                resp.raise_for_status()
                input_text = resp.text # 본문가져오기

            except Exception:
                conversion.status_fail() # status 실패처리 모델메서드
                return Response({"상태": conversion.status, "결과": conversion.result}, status=status.HTTP_200_OK)

        try:
            # "gpt-4o-mini" 불러오기
            conversion.status_processing() # status 진행중으로 변경 모델메서드
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {'role': 'system', "content": ("너는 경계선 지능인을 위해 어려운 글을 이해하기 쉬운 글로 만들어 주는 도우미, 모르는 말이 있으면 뜻을 함께 써줘. 바꾼 글만 보여주고 바뀐글은 5줄 이내로 정리. 문장은 짧게 써.")},
                    {'role':'user','content': input_text}
                ]
            )
            # 성공
            conversion.status_done(completion.choices[0].message.content)
            return Response(ConversionSerializer(conversion).data, status=status.HTTP_201_CREATED)
        
        except Exception:
            conversion.status_fail()
            return Response({"상태": conversion.status, "결과": conversion.result}, status=status.HTTP_200_OK)