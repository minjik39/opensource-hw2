from pydantic import BaseModel, Field

class SentimentRequest(BaseModel):
    text: str = Field(..., title="분석할 문장", example="이 영화 정말 최고였어요! 다시 보고 싶네요.")

class SentimentResponse(BaseModel):
    label: str = Field(..., title="감정 레이블 (예: POSITIVE, NEGATIVE)")
    score: float = Field(..., title="예측 신뢰도 (0.0 ~ 1.0)")
