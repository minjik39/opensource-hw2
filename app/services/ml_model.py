from transformers import pipeline
import math

class SentimentModel:
    def __init__(self):
        # 실제 존재하는 한국어 감정 분류 모델 (공포, 놀람, 분노, 슬픔, 중립, 행복, 혐오)
        self.model_name = "Seonghaa/korean-emotion-classifier-roberta"
        print(f"[{self.model_name}] 모델을 로딩 중입니다...")
        
        try:
            self.classifier = pipeline(
                "text-classification", 
                model=self.model_name, 
                return_all_scores=True
            )
            print("모델 로딩 완료.")
        except Exception as e:
            print(f"모델 로딩 실패. 에러: {e}")
            raise e

    def _map_score_to_intensity(self, score: float) -> int:
        """확률값(0~1)을 1~5 정수 강도로 변환합니다."""
        if score <= 0.2: return 1
        if score <= 0.4: return 2
        if score <= 0.6: return 3
        if score <= 0.8: return 4
        return 5

    def predict(self, text: str) -> dict:
        # top_k=None을 설정하면 항상 모든 감정의 점수를 리스트 형태로 반환합니다.
        results = self.classifier(text, top_k=None)[0]
        
        # 모델의 실제 라벨: 0:공포, 1:놀람, 2:분노, 3:슬픔, 4:중립, 5:행복, 6:혐오
        intensities = {}
        top_val = -1
        top_emotion = "중립"
        conf_score = 0
        
        for res in results:
            # 이제 res는 확실히 {'label': '...', 'score': ...} 형태의 딕셔너리입니다.
            label = res['label']
            score = res['score']
            
            if label == "중립":
                continue
                
            intensity = self._map_score_to_intensity(score)
            intensities[label] = intensity
            
            if score > top_val:
                top_val = score
                top_emotion = label
                conf_score = round(score, 4)
        
        return {
            "top_emotion": top_emotion,
            "intensities": intensities,
            "score": conf_score
        }

sentiment_model = SentimentModel()
