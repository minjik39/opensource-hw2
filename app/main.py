from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
from app.models.schemas import SentimentRequest, SentimentResponse
from app.services.ml_model import sentiment_model

app = FastAPI(
    title="Sentiment Analysis API",
    description="MLOps 파이프라인을 위한 문장 감정 분석 API 서버 (FastAPI)",
    version="1.0.0"
)

# 현재 파일 위치를 기준으로 index.html 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_FILE = os.path.join(BASE_DIR, "index.html")

@app.get("/")
def read_root():
    """루트 경로 접속 시 예쁜 웹 프론트엔드를 보여줍니다."""
    if os.path.exists(FRONTEND_FILE):
        return FileResponse(FRONTEND_FILE)
    return {"message": "index.html 파일을 찾을 수 없습니다."}

@app.post("/predict", response_model=SentimentResponse)
def predict_sentiment(request: SentimentRequest):
    """
    입력된 텍스트의 6가지 감정 강도를 예측합니다.
    """
    try:
        # 비어있는 문장 등에 대한 기본적인 방어 코드
        if not request.text or not request.text.strip():
            return SentimentResponse(top_emotion="중립", intensities={}, score=0.0)

        result = sentiment_model.predict(request.text)
        return SentimentResponse(
            top_emotion=result.get("top_emotion", "중립"), 
            intensities=result.get("intensities", {}), 
            score=result.get("score", 0.0)
        )
    except Exception as e:
        # 엔드포인트 차원에서의 예외 처리
        print(f"[API ERROR] {str(e)}")
        return SentimentResponse(top_emotion="에러 발생", intensities={}, score=0.0)
