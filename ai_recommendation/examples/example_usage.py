"""
모델 로더 사용 예시
서버에서 어떻게 사용하는지 보여주는 예제입니다.
"""

import sys
import os

# 상위 디렉터리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_loader import get_model_loader
import numpy as np

def example_basic_usage():
    """기본 사용 예시"""
    print("=" * 50)
    print("모델 로더 기본 사용 예시")
    print("=" * 50)
    
    # 모델 로드 (서버 시작 시 한 번만)
    print("\n[1] 모델 로드 중...")
    model_loader = get_model_loader()
    print("  ✓ 모델 로드 완료")
    
    # 파라미터 확인
    params = model_loader.get_params()
    print(f"\n[2] 파라미터:")
    print(f"  - w2v_vector_size: {params['w2v_vector_size']}")
    print(f"  - cf_vector_size: {params['cf_vector_size']}")
    print(f"  - color_weight: {params['color_weight']}")
    print(f"  - fabric_weight: {params['fabric_weight']}")
    
    # 데이터 확인
    merged_df = model_loader.get_merged_df()
    print(f"\n[3] 데이터:")
    print(f"  - 병합 데이터 개수: {len(merged_df)}")
    print(f"  - 컬럼: {list(merged_df.columns)}")
    
    # 벡터 가져오기 예시
    print("\n[4] 벡터 변환 예시:")
    token = "상의_white_cotton_반소매 티셔츠_남성_여름_casual"
    vector = model_loader.get_w2v_vector(token)
    print(f"  - 토큰: {token}")
    print(f"  - 벡터 shape: {vector.shape}")
    print(f"  - 벡터 (처음 5개): {vector[:5]}")
    
    # 색상/재질 벡터 예시
    color_vec = model_loader.get_color_vector("white")
    fabric_vec = model_loader.get_fabric_vector("cotton")
    print(f"\n[5] 색상/재질 벡터:")
    print(f"  - 색상 'white' 벡터 shape: {color_vec.shape}")
    print(f"  - 재질 'cotton' 벡터 shape: {fabric_vec.shape}")
    
    # 문장 벡터 변환 예시
    tokens = ["상의_white_cotton_반소매", "티셔츠_남성_여름", "casual"]
    sentence_vec = model_loader.sentence_to_vector(tokens)
    print(f"\n[6] 문장 벡터 변환:")
    print(f"  - 토큰 리스트: {tokens}")
    print(f"  - 문장 벡터 shape: {sentence_vec.shape}")
    
    print("\n" + "=" * 50)
    print("예시 완료!")
    print("=" * 50)


def example_server_integration():
    """서버 통합 예시 (의사 코드)"""
    print("\n" + "=" * 50)
    print("서버 통합 예시 (의사 코드)")
    print("=" * 50)
    
    print("""
# FastAPI 예시

from fastapi import FastAPI
from ai_recommendation.model_loader import get_model_loader
from ai_recommendation.recommendation_engine import recommend_outfit

app = FastAPI()

# 서버 시작 시 모델 로드
@app.on_event("startup")
async def load_models():
    global model_loader
    model_loader = get_model_loader()
    print("✓ 모델 로드 완료")

# API 엔드포인트
@app.post("/recommend")
async def recommend(request_data: dict):
    result = recommend_outfit(
        selected_items=request_data['selected_items'],
        available_items=request_data['available_items'],
        model_loader=model_loader
    )
    return result
    """)


if __name__ == "__main__":
    # 기본 사용 예시 실행
    try:
        example_basic_usage()
        example_server_integration()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n먼저 train_model.py를 실행하여 모델을 학습하고 저장하세요.")

