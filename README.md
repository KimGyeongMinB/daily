# Daily: 어제보다 더 나은 나를 위한 기록

> **"완벽한 코드는 없지만, 어제보다 나은 코드는 있다고 믿습니다."**

Daily 는 제가 매일 한 줄의 코드를 더하며, 단순한 기능 구현을 넘어 백엔드 엔지니어로서 갖춰야 할 '기본기'와 '안정성'을 체득하는 과정에 집중하고 있습니다.
---

## 프로젝트를 진행하는 이유
### 1. 매일 조금씩 진행하면서 매일 조금씩 발전하는 것을 목표로 합니다.
### 2. 내가 만든 코드가 서비스에 부정적인 영향이 끼치지 않기 위해 진행하고 있습니다.

⚙️ How to Run
이 프로젝트는 Local 가상환경에서 테스트하거나, Docker를 통해 전체 스택을 한 번에 실행할 수 있습니다.

1. 가상환경 설정 및 패키지 설치 (Local Test용)
도커 없이 로컬에서 코드를 확인하거나 수정할 때 필요합니다.

Bash
# 1. 저장소 클론
git clone https://github.com/사용자계정/daily.git
cd daily

# 2. 가상환경 생성 및 활성화
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. 필수 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt
2. 환경 변수(.env) 설정 (필수)
프로젝트 루트 폴더에 .env 파일을 생성하고, .env.example의 내용을 참고하여 본인의 키값을 입력해야 합니다.

파일명: .env

필수 입력 항목: OPEN_API_KEY, DJANGO_SECRET_KEY, EMAIL_ID, EMAIL_PW 등

3. Docker를 이용한 전체 실행 (권장)
Docker가 설치되어 있다면 아래 명령어로 별도의 설정 없이 DB, Redis, Celery를 포함한 모든 환경을 구동할 수 있습니다.

Bash
# 1. 컨테이너 빌드 및 백그라운드 실행
docker-compose up -d --build

# 2. DB 테이블 생성 (최초 실행 시 필수)
docker-compose exec backend python manage.py migrate
4. 접속 및 확인
Main Service (API): http://localhost:8000

Swagger Documentation: http://localhost:8000/api/schema/swagger-ui/

Tip: Swagger 페이지에서 AI 글 변환 API를 직접 테스트해 볼 수 있습니다.

## 주요 Directory
daily
  ├─ accounts/ # 계정    
  │  ├─ auth.py # 인증
  │  ├─ models.py # 모델
  │  ├─ tasks.py # Celery 비동기 발송 태스크
  │  ├─ utils.py # 공통 유틸
  │  ├─ views.py # 회원가입, 로그인, 로그아웃 API
  │  └─ __init__.py
  ├─ compose.yaml  # 도커 컨테이너 설정          
  ├─ config/
  │  ├─ celery.py # celery
  │  ├─ settings.py # setting
  ├─ conversions # AI 기반 글 변환
  │  ├─ models.py # 모델
  │  ├─ views.py # GPT-4o-mini 연동 API
  │  └─ __init__.py
  ├─ Dockerfile # 도커파일
  └─ requirements.txt # 의존성 라이브러리

## Tech Stack
* **Framework:** Django, Django Rest Framework (DRF)
* **AI:** OpenAI API (gpt-4o-mini)
* **Web Scraping:** BeautifulSoup4
* **Database:** PostgreSQL
* **Task Queue:** Celery, Redis
* **Auth:** SimpleJWT (Cookie based)
* **Infrastructure:** Docker, Docker-compose
* **API Docs:** drf-spectacular

## 기능구현

## conversions
### AI 기반 글 변환
* **주제 선정 이유:** 과거 경계선 지능인을 위한 서비스 관련 공모전을 준비했으나, 개인적인 사정으로 끝까지 완수하지 못했던 아쉬움이 있었습니다. 그때의 고민을 백엔드 기술로 직접 구현해 보고자 이 주제를 선정하게 되었습니다.
* **적용 모델:** gpt-4o-mini
* **처리과정:** 사용자가 직접 입력한 텍스트를 우선 처리, URL만 제공될 경우 BeautifulSoup4를 활용해 웹 페이지의 본문을 자동으로 크롤링하여 원문을 확보

## accounts
### JWT
* **문제점:** 토큰을 localstorage 에 저장할 경우 XSS(악성 자바스크립트 코드) 를 통해 쉽게 탈취, 무상태(Stateless)의 단점인 서버에서 강제 무효화 못하는 문제
* **해결방법**
  1) 토큰을 HttpOnly Cookie 에 저장하여 접근을 막고, Secure = True(현재 개발중 이므로 = False)을 통해  HTTPS 에서만 토큰이 전송되게 설정
  2) 쿠키형식으로 발생하는 CSRF 공격 SameSite=Lax 설정으로 완화
  3) access_token 은 짧은시간(5분), refresh_token 은 사용시 blacklist 에 등록해 재사용 방지

### 이메일전송
* **문제점:** 회원가입 후 이메일을 전송할 시 응답이 3~5초 걸리는 문
* **해결방법**
  Celery라는 비동기 작업 큐를 사용하여 worker에서 delay 메서드를 통해 백그라운드에서 처리하도록 구현

### 도커(Docker) 사용
* **문제점:** 내 Pc 에서만 아니라 어떤 환경에서도 코드가 똑같이 안전하게 돌아가게 하고 싶었습니다.
* **해결방법**
  Docker-compose를 설치해 backend, db, redis, worker 4가지의 컨테이너를 띄어 관리
* **보완해야할 부분**
  도커를 처음 사용하다 보니 처음 접해보는 개념 및 명령어들이 많이 어려움을 겪었으며 이에따라 블로그, 공식문서, ai 툴(chat gpt, gemini) 등을 활용해 해결
  이에 따라 이것들을 안찾고 사용할 수 있는 수준까지 보완필요
  
### 트랜잭션 사용
* **문제점:** 여러 DB 작업이 동시에 일어날 경우 데이터가 중복되서 실행이 되지 않거나 꼬이는 경우가 발생할 수 있음
* **해결방법**
  django.db 의 transaction 을 이용해 동시에 일어날 수 있는 상황을 방지해 고립성을 보장 및 실패치 자동으로 롤백하여 원자성 보장
