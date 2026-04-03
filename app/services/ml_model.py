from transformers import pipeline

class SentimentModel:
    def __init__(self):
        # MLOps 파이프라인에서 모델을 로드하는 부분을 캡슐화합니다.
        # 한국어 텍스트에 강점을 가진 Hugging Face 모델 지정 (예: KoBERT, KcELECTRA 등)
        # 이번 예제에서는 다국어 감정 분석을 지원하는 모델 중 하나를 기본값으로 사용합니다.
        self.model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        print(f"[{self.model_name}] 모델을 로딩 중입니다...")
        
        try:
            # 첫 실행 시 모델을 로컬에 다운로드합니다. 
            self.classifier = pipeline("sentiment-analysis", model=self.model_name)
            print("모델 로딩 완료.")
        except Exception as e:
            print(f"모델 로딩 실패. 기본 모델로 대체합니다. 에러: {e}")
            self.classifier = pipeline("sentiment-analysis")

    def predict(self, text: str) -> dict:
        """
        입력된 문장의 감정을 분석하여 결과를 반환합니다.
        """
        # pipeline은 기본적으로 리스트 형태를 반환하므로 첫 번째 요소 추출
        prediction = self.classifier(text)[0]
        
        # nlptown 모델의 경우 별점(1 star ~ 5 stars)을 반환하므로 
        # 이를 좀 더 직관적인 POSITIVE / NEGATIVE 로 매핑해주는 로직을 추가할 수 있습니다.
        # 여기서는 원본 결과를 그대로 반환합니다.
        return {
            "label": prediction["label"],
            "score": round(prediction["score"], 4)
        }

# 애플리케이션 시작 시 싱글톤 패턴으로 모델을 한 번만 메모리에 올립니다.
sentiment_model = SentimentModel()
