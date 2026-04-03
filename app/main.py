from fastapi import FastAPI
from app.models.schemas import SentimentRequest, SentimentResponse
from app.services.ml_model import sentiment_model

app = FastAPI(
    title="Sentiment Analysis API",
    description="MLOps 파이프라인을 위한 문장 감정 분석 API 서버 (FastAPI)",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Sentiment Analysis API 서버가 정상적으로 실행 중입니다."}

@app.post("/predict", response_model=SentimentResponse)
def predict_sentiment(request: SentimentRequest):
    """
    입력된 텍스트의 감정을 예측합니다.
    """
    result = sentiment_model.predict(request.text)
    return SentimentResponse(label=result["label"], score=result["score"])
