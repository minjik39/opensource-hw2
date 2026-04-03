from transformers import pipeline
import math

class SentimentModel:
    def __init__(self):
        # 한국어 7개 감정(행복, 슬픔, 분노, 공포, 놀람, 혐오, 중립) 분류 모델
        self.model_name = "Seonghaa/koelectra-base-v3-discriminator-finetuned-emotion"
        print(f"[{self.model_name}] 모델을 로딩 중입니다...")
        
        try:
            # CPU 환경 기준 성능을 위해 return_all_scores=True 설정
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
        """
        입력된 문장의 6가지 감정 강도를 분석하여 반환합니다. 
        (중립 제외, 행복/슬픔/분노/공포/혐오/놀람 포함)
        """
        results = self.classifier(text)[0]
        
        # 모델 출력 라벨 정보:
        # 0: 공포, 1: 놀람, 2: 분노, 3: 슬픔, 4: 중립, 5: 행복, 6: 혐오
        mapping = {
            "공포": "fear", "놀람": "surprise", "분노": "anger", 
            "슬픔": "sadness", "중립": "neutral", "행복": "happiness", "혐오": "disgust"
        }
        
        intensities = {}
        top_val = -1
        top_emotion = "중립"
        conf_score = 0
        
        for res in results:
            label = res['label'] # 모델이 '행복', '분노' 등 한국어 라벨을 직접 뱉음
            score = res['score']
            
            if label == "중립":
                continue # 중립 감정은 강도 산출에서 제외
                
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

# 싱글톤 패턴
sentiment_model = SentimentModel()
