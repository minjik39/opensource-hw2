from transformers import pipeline

class SentimentModel:
    def __init__(self):
        # 은어/구어체를 잘 파악하는 한국어 전용 감정 모델 (KcELECTRA 기반)
        self.model_name = "PongKorea/emotion_kcelectra"
        print(f"[{self.model_name}] 모델을 로딩 중입니다...")
        
        try:
            self.classifier = pipeline(
                "text-classification", 
                model=self.model_name
            )
            print("모델 로딩 완료.")
            
            # 모델의 세분화된 라벨들을 기존 UI의 6가지 척도로 그룹화
            self.emotion_grouping = {
                '행복': ['즐거운', '벅찬', '평온'],
                '슬픔': ['슬픔', '비탄', '시무룩'],
                '분노': ['화가나는', '격분한', '짜증스러운'],
                '공포': ['공포', '불안', '긴장초조'],
                '혐오': ['혐오스러운', '역겨운', '불쾌한'],
                '놀람': [] # 직접 매칭되는 라벨 부재
            }
        except Exception as e:
            print(f"모델 로딩 실패. 에러: {e}")
            raise e

    def _map_score_to_intensity(self, score: float) -> int:
        """확률값(0~1)을 1~10 정수 강도로 변환합니다."""
        val = int(round(score * 10))
        return max(1, min(10, val))

    def predict(self, text: str) -> dict:
        try:
            raw_results = self.classifier(text, top_k=None)
            
            if isinstance(raw_results, list) and len(raw_results) > 0:
                results = raw_results[0]
            else:
                results = raw_results
            
            if isinstance(results, dict):
                results = [results]
            
            # 6가지 기본 감정의 점수를 저장할 변수
            grouped_scores = {"행복": 0.0, "슬픔": 0.0, "분노": 0.0, "공포": 0.0, "혐오": 0.0, "놀람": 0.0}
            
            for res in results:
                if not isinstance(res, dict): continue
                    
                label = res.get('label', 'Unknown')
                score = res.get('score', 0.0)
                
                # 라벨 그룹핑에 따라 최대 점수를 할당
                for target_emotion, keywords in self.emotion_grouping.items():
                    if label in keywords:
                        grouped_scores[target_emotion] = max(grouped_scores[target_emotion], score)
            
            intensities = {}
            top_val = -1
            top_emotion = "중립"
            conf_score = 0
            
            for emotion, score in grouped_scores.items():
                intensity = self._map_score_to_intensity(score)
                intensities[emotion] = intensity
                
                if score > top_val:
                    top_val = score
                    top_emotion = emotion
                    conf_score = round(score, 4)
            
            # 기준 확률 이하일 경우 중립
            if top_val < 0.2:
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
