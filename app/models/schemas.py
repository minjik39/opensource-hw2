from pydantic import BaseModel, Field
from typing import Dict, Optional

class SentimentRequest(BaseModel):
    text: str = Field(..., title="분석할 문장", example="오늘 친구들과 맛있는 음식을 먹어서 너무 행복해!")

class SentimentResponse(BaseModel):
    top_emotion: str = Field(default="중립", title="지배적인 감정", example="행복")
    intensities: Dict[str, int] = Field(
        default_factory=dict, 
        title="감정별 강도 (1~10)", 
        example={"행복": 10, "슬픔": 1, "분노": 1, "공포": 1, "혐오": 1, "놀람": 1}
    )
    score: float = Field(default=0.0, title="예측 신뢰도 (0.0 ~ 1.0)")
