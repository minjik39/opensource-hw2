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
        try:
            # top_k=None을 설정하면 최대한 모든 감정의 점수를 리스트 형태로 반환 시도
            raw_results = self.classifier(text, top_k=None)
            
            # 입력 데이터가 리스트로 올 경우 [[...]] 형태이므로 첫 번째 요소를 추출
            if isinstance(raw_results, list) and len(raw_results) > 0:
                results = raw_results[0]
            else:
                results = raw_results
            
            # 여기서 results가 만약 딕셔너리 하나라면 리스트로 감싸서 루프를 돌 수 있게 함
            if isinstance(results, dict):
                results = [results]
            
            # 로깅: 디버깅용으로 실제 어떤 형태의 데이터가 들어오는지 출력
            # (이 정보는 docker logs mlops-api-container 명령어로 확인 가능)
            print(f"[DEBUG] Raw Inference Results Type: {type(results)}, Content: {results}")

            intensities = {}
            top_val = -1
            top_emotion = "중립"
            conf_score = 0
            
            for res in results:
                # 딕셔너리인지 한 번 더 확인 (TypeError 방지)
                if not isinstance(res, dict):
                    print(f"[WARNING] res is not a dict: {res} (type: {type(res)})")
                    continue
                    
                label = res.get('label', 'Unknown')
                score = res.get('score', 0.0)
                
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
            
        except Exception as e:
            # 예상치 못한 에러 발생 시 로그를 남기고 빈 결과를 반환하여 서버 다운 방지
            print(f"[ERROR] Inference failed for text '{text}': {str(e)}")
            return {
                "top_emotion": "중립",
                "intensities": {},
                "score": 0.0
            }

sentiment_model = SentimentModel()
