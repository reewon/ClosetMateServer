"""
모델 학습 및 저장 스크립트
데이터를 로드하여 Word2Vec 모델을 학습하고, 필요한 데이터를 저장합니다.
서버 시작 전에 한 번만 실행하면 됩니다.
"""

import pandas as pd
import numpy as np
import os
import pickle
import json
from gensim.models import Word2Vec

# ===================================
# 파라미터 설정
# ===================================
w2v_vector_size = 100      # 문장 임베딩 차원 수
cf_vector_size = 20       # color/fabric 임베딩 차원 수
color_weight = 0.8        # 색상 벡터 가중치
fabric_weight = 0.2       # 재질 벡터 가중치

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def has_all_required_categories(tokens):
    """필수 카테고리(상의, 하의, 신발)가 모두 있는지 확인"""
    categories = {"상의": False, "하의": False, "신발": False}
    for token in tokens:
        for category in categories:
            if token.startswith(category):
                categories[category] = True
    return all(categories.values())

def sentence_to_vector(tokens, w2v_model, vector_size):
    """문장을 벡터로 변환"""
    vectors = [w2v_model.wv[word] for word in tokens if word in w2v_model.wv]
    return np.mean(vectors, axis=0) if vectors else np.zeros(vector_size)

def get_color_vector(color, color_fabric_model, vector_size):
    """색상 벡터 추출"""
    if isinstance(color, str) and color.lower() in color_fabric_model.wv:
        return color_fabric_model.wv[color.lower()]
    else:
        return np.zeros(vector_size)

def get_fabric_vector(fabric, color_fabric_model, vector_size):
    """재질 벡터 추출"""
    if isinstance(fabric, str) and fabric.lower() in color_fabric_model.wv:
        return color_fabric_model.wv[fabric.lower()]
    else:
        return np.zeros(vector_size)

def main():
    print("=" * 50)
    print("모델 학습 시작")
    print("=" * 50)
    
    # ===================================
    # 1. 데이터 로드 및 필터링
    # ===================================
    print("\n[1/6] 데이터 로드 중...")
    sentence_file = os.path.join(DATA_DIR, "sentence_comb_fin.csv")
    category_file = os.path.join(DATA_DIR, "total_final_data.csv")
    
    if not os.path.exists(sentence_file):
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {sentence_file}")
    if not os.path.exists(category_file):
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {category_file}")
    
    df = pd.read_csv(sentence_file)
    df['tokens'] = df['w2v_sentence'].apply(lambda x: x.split())
    
    filtered_df = df[df['tokens'].apply(has_all_required_categories)].reset_index(drop=True)
    filtered_df = filtered_df.drop(columns=['tokens'])
    print(f"  ✓ 필터링된 데이터: {len(filtered_df)}개")
    
    category_df = pd.read_csv(category_file)
    print(f"  ✓ 카테고리 데이터: {len(category_df)}개")
    
    # ===================================
    # 2. 데이터 병합
    # ===================================
    print("\n[2/6] 데이터 병합 중...")
    merged_df = pd.merge(
        filtered_df,
        category_df[['coord_id', 'predicted_color', 'predicted_fabric']],
        on='coord_id',
        how='inner'
    )
    print(f"  ✓ 병합된 데이터: {len(merged_df)}개")
    
    # ===================================
    # 3. 문장 토큰화 및 Word2Vec 모델 학습
    # ===================================
    print("\n[3/6] Word2Vec 모델 학습 중...")
    merged_df['tokens'] = merged_df['w2v_sentence'].apply(lambda x: x.split())
    tokenized_sentences = merged_df['tokens'].tolist()
    
    w2v_model = Word2Vec(
        sentences=tokenized_sentences,
        vector_size=w2v_vector_size,
        window=5,
        min_count=1,
        workers=4,
        seed=42
    )
    print(f"  ✓ Word2Vec 모델 학습 완료 (vocab size: {len(w2v_model.wv)})")
    
    # ===================================
    # 4. 문장 벡터 생성
    # ===================================
    print("\n[4/6] 문장 벡터 생성 중...")
    merged_df['w2v_vector'] = merged_df['tokens'].apply(
        lambda tokens: sentence_to_vector(tokens, w2v_model, w2v_vector_size)
    )
    print("  ✓ 문장 벡터 생성 완료")
    
    # ===================================
    # 5. Color/Fabric Word2Vec 모델 학습
    # ===================================
    print("\n[5/6] Color/Fabric Word2Vec 모델 학습 중...")
    fabric_color_tokens = category_df[['predicted_color', 'predicted_fabric']].astype(str).values.tolist()
    fabric_color_tokens = [[str(token).lower()] for row in fabric_color_tokens for token in row]
    
    color_fabric_model = Word2Vec(
        sentences=fabric_color_tokens,
        vector_size=cf_vector_size,
        window=2,
        min_count=1,
        workers=4,
        seed=42
    )
    print(f"  ✓ Color/Fabric 모델 학습 완료 (vocab size: {len(color_fabric_model.wv)})")
    
    # ===================================
    # 6. 색상/재질 벡터 및 최종 벡터 생성
    # ===================================
    print("\n[6/6] 최종 벡터 생성 중...")
    merged_df['color_vector'] = merged_df['predicted_color'].apply(
        lambda color: get_color_vector(color, color_fabric_model, cf_vector_size)
    )
    merged_df['fabric_vector'] = merged_df['predicted_fabric'].apply(
        lambda fabric: get_fabric_vector(fabric, color_fabric_model, cf_vector_size)
    )
    
    # 최종 벡터 생성 (w2v + color + fabric)
    final_vectors = []
    for i in range(len(merged_df)):
        w2v = merged_df.iloc[i]['w2v_vector']
        color_vec = merged_df.iloc[i]['color_vector'] * color_weight
        fabric_vec = merged_df.iloc[i]['fabric_vector'] * fabric_weight
        final_vector = np.concatenate([w2v, color_vec, fabric_vec])
        final_vectors.append(final_vector)
    
    merged_df['final_vector'] = final_vectors
    print("  ✓ 최종 벡터 생성 완료")
    
    # ===================================
    # 7. 모델 및 데이터 저장
    # ===================================
    print("\n" + "=" * 50)
    print("모델 및 데이터 저장 중...")
    print("=" * 50)
    
    # Word2Vec 모델 저장
    w2v_model_path = os.path.join(MODEL_DIR, "w2v_model.model")
    w2v_model.save(w2v_model_path)
    print(f"  ✓ Word2Vec 모델 저장: {w2v_model_path}")
    
    # Color/Fabric 모델 저장
    color_fabric_model_path = os.path.join(MODEL_DIR, "color_fabric_model.model")
    color_fabric_model.save(color_fabric_model_path)
    print(f"  ✓ Color/Fabric 모델 저장: {color_fabric_model_path}")
    
    # 전처리된 데이터 저장 (벡터 포함)
    merged_df_path = os.path.join(MODEL_DIR, "merged_df.pkl")
    with open(merged_df_path, 'wb') as f:
        pickle.dump(merged_df, f)
    print(f"  ✓ 병합 데이터 저장: {merged_df_path}")
    
    # 필터링된 데이터 저장
    filtered_df_path = os.path.join(MODEL_DIR, "filtered_df.pkl")
    with open(filtered_df_path, 'wb') as f:
        pickle.dump(filtered_df, f)
    print(f"  ✓ 필터링 데이터 저장: {filtered_df_path}")
    
    # 파라미터 저장
    params = {
        'w2v_vector_size': w2v_vector_size,
        'cf_vector_size': cf_vector_size,
        'color_weight': color_weight,
        'fabric_weight': fabric_weight
    }
    params_path = os.path.join(MODEL_DIR, "params.json")
    with open(params_path, 'w', encoding='utf-8') as f:
        json.dump(params, f, indent=2, ensure_ascii=False)
    print(f"  ✓ 파라미터 저장: {params_path}")
    
    print("\n" + "=" * 50)
    print("모델 학습 및 저장 완료!")
    print("=" * 50)
    print(f"\n저장 위치: {MODEL_DIR}/")
    print("\n다음 파일들이 생성되었습니다:")
    print("  - w2v_model.model")
    print("  - color_fabric_model.model")
    print("  - merged_df.pkl")
    print("  - filtered_df.pkl")
    print("  - params.json")

if __name__ == "__main__":
    main()

