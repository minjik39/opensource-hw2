FROM python:3.11-slim

# 환경 변수 설정
# PYTHONDONTWRITEBYTECODE: 파이썬이 .pyc 파일을 쓰지 않도록 설정
# PYTHONUNBUFFERED: 파이썬 출력이 버퍼링 없이 즉시 콘솔에 출력되도록 설정 (로그 확인 용이)
# HF_HOME: Hugging Face 모델이 저장될 캐시 디렉터리 지정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/models

# 작업 디렉터리 설정
WORKDIR /app

# 가장 자주 변경되지 않는 의존성 파일을 먼저 복사하여 도커 레이어 캐시 활용
COPY requirements.txt .

# 불필요한 캐시 없이 패키지 설치 (이미지 경량화)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사 (app 폴더)
COPY ./app ./app

# 🔥 도커 빌드 시점에 모델을 미리 다운로드하여 이미지에 내장 
# -> 이를 통해 컨테이너가 켜질 때 모델을 다운받는 시간을 획기적으로 없애고, (Cold Start 방지)
# -> 폐쇄망(Offline) 환경 등 인터넷이 없는 환경에서도 컨테이너를 실행할 수 있게 최적화
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='Seonghaa/koelectra-base-v3-discriminator-finetuned-emotion')"

# 서버 포트 노출
EXPOSE 8000

# 컨테이너 실행 시 Uvicorn 서버 구동
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
