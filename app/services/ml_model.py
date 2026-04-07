from transformers import pipeline

class SentimentModel:
    def __init__(self):
        # 은어('개웃기네')까지 문맥을 완벽하게 파악하는 다국어 Zero-shot 분석 모델
        self.model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        print(f"[{self.model_name}] 모델을 로딩 중입니다... (Zero-shot)")
        
        try:
            self.classifier = pipeline(
                "zero-shot-classification", 
                model=self.model_name
            )
            print("모델 로딩 완료.")
        except Exception as e:
            print(f"모델 로딩 실패. 에러: {e}")
            raise e

    def _map_score_to_intensity(self, score: float) -> int:
        """확률값(0~1)을 1~5 정수 강도로 변환합니다."""
        if score <= 0.15: return 1
        if score <= 0.30: return 2
        if score <= 0.45: return 3
        if score <= 0.60: return 4
        return 5

    def predict(self, text: str) -> dict:
        try:
            # 6가지 후보 감정을 주고 문장과 가장 잘 어울리는지 확률을 매깁니다.
            candidate_labels = ["행복", "슬픔", "분노", "공포", "놀람", "혐오"]
            
            # multi_label=False는 각 확률의 합이 1이 되도록 만듭니다. multi_label=True면 각각의 독립 확률(sigmoid)
            results = self.classifier(text, candidate_labels=candidate_labels, multi_label=True)
            
            intensities = {}
            top_val = -1
            top_emotion = "중립"
            conf_score = 0
            
            labels = results['labels']
            scores = results['scores']
            
            for label, score in zip(labels, scores):
                intensity = self._map_score_to_intensity(score)
                intensities[label] = intensity
                
                if score > top_val:
                    top_val = score
                    top_emotion = label
                    conf_score = round(score, 4)
            
            # 모든 점수가 너무 낮으면 중립 처리
            if top_val < 0.3:
                top_emotion = "중립"
            
            return {
                "top_emotion": top_emotion,
                "intensities": intensities,
                "score": conf_score
            }
            
        except Exception as e:
            print(f"[ERROR] Inference failed for text '{text}': {str(e)}")
            return {"top_emotion": "중립", "intensities": {}, "score": 0.0}

sentiment_model = SentimentModel()
