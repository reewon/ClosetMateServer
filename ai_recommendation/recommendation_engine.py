"""
추천 엔진 모듈
API 요청 시 추천 로직을 실행하여 코디를 추천합니다.
"""

import numpy as np
from typing import Dict, List, Optional, Any
from sklearn.metrics.pairwise import cosine_similarity
from .model_loader import ModelLoader


def parse_feature(feature: str) -> Dict[str, str]:
    """
    Feature 문자열을 파싱합니다.
    
    형식: 카테고리_색상_재질_상세정보_성별_계절_스타일
    
    Args:
        feature: Feature 문자열
        
    Returns:
        Dict: 파싱된 정보 (category, color, fabric, detail, gender, season, style)
    """
    parts = feature.split('_')
    if len(parts) < 7:
        # 형식이 맞지 않으면 기본값 반환
        return {
            'category': parts[0] if parts else '',
            'color': parts[1] if len(parts) > 1 else '',
            'fabric': parts[2] if len(parts) > 2 else '',
            'detail': parts[3] if len(parts) > 3 else '',
            'gender': parts[4] if len(parts) > 4 else '',
            'season': parts[5] if len(parts) > 5 else '',
            'style': parts[6] if len(parts) > 6 else ''
        }
    
    return {
        'category': parts[0],
        'color': parts[1],
        'fabric': parts[2],
        'detail': parts[3],
        'gender': parts[4],
        'season': parts[5],
        'style': parts[6] if len(parts) > 6 else ''  # casual, minimal, street, sporty 중 하나
    }


def feature_to_tokens(feature: str) -> List[str]:
    """
    Feature 문자열을 토큰 리스트로 변환합니다.
    
    Args:
        feature: Feature 문자열
        
    Returns:
        List[str]: 토큰 리스트
    """
    # 공백으로 split하여 토큰화
    return feature.replace('_', ' ').split()


def item_to_vector(feature: str, model_loader: ModelLoader) -> np.ndarray:
    """
    아이템의 feature를 벡터로 변환합니다.
    
    Args:
        feature: Feature 문자열
        model_loader: 모델 로더 인스턴스
        
    Returns:
        np.ndarray: 최종 벡터
    """
    parsed = parse_feature(feature)
    params = model_loader.get_params()
    
    # 토큰화
    tokens = feature_to_tokens(feature)
    
    # Word2Vec 벡터
    w2v_vector = model_loader.sentence_to_vector(tokens)
    
    # 색상 벡터
    color_vector = model_loader.get_color_vector(parsed['color']) * params['color_weight']
    
    # 재질 벡터
    fabric_vector = model_loader.get_fabric_vector(parsed['fabric']) * params['fabric_weight']
    
    # 최종 벡터 결합
    final_vector = np.concatenate([w2v_vector, color_vector, fabric_vector])
    
    return final_vector


def category_mapping(category: str) -> str:
    """
    카테고리 이름을 매핑합니다.
    
    Args:
        category: 카테고리 이름 (한글 또는 영문)
        
    Returns:
        str: 영문 카테고리 이름
    """
    mapping = {
        '상의': 'top',
        'top': 'top',
        '하의': 'bottom',
        'bottom': 'bottom',
        '신발': 'shoes',
        'shoes': 'shoes',
        '아우터': 'outer',
        'outer': 'outer'
    }
    return mapping.get(category, category)


def find_best_match(
    target_vector: np.ndarray,
    merged_df,
    selected_categories: List[str],
    model_loader: ModelLoader
) -> Optional[Dict[str, Any]]:
    """
    merged_df에서 가장 유사한 코디를 찾습니다.
    
    Args:
        target_vector: 타겟 벡터
        merged_df: 병합된 데이터프레임
        selected_categories: 이미 선택된 카테고리 리스트
        model_loader: 모델 로더 인스턴스
        
    Returns:
        Optional[Dict]: 가장 유사한 코디 정보 (없으면 None)
    """
    if merged_df is None or len(merged_df) == 0:
        return None
    
    # 코디 벡터들 추출
    coord_vectors = np.array(merged_df['final_vector'].tolist())
    
    # 코사인 유사도 계산
    similarities = cosine_similarity([target_vector], coord_vectors)[0]
    
    # 가장 유사한 코디 찾기
    best_idx = np.argmax(similarities)
    best_similarity = similarities[best_idx]
    
    # 유사도가 너무 낮으면 None 반환
    if best_similarity < 0.3:
        return None
    
    best_coord = merged_df.iloc[best_idx]
    
    return {
        'coord_id': best_coord.get('coord_id', None),
        'w2v_sentence': best_coord.get('w2v_sentence', ''),
        'similarity': float(best_similarity)
    }


def recommend_category(
    category: str,
    available_items: List[Dict[str, Any]],
    target_vector: np.ndarray,
    merged_df,
    model_loader: ModelLoader
) -> Optional[int]:
    """
    특정 카테고리의 아이템을 추천합니다.
    
    Args:
        category: 카테고리 이름 ('top', 'bottom', 'shoes', 'outer')
        available_items: 선택 가능한 아이템 리스트
        target_vector: 타겟 벡터
        merged_df: 병합된 데이터프레임
        model_loader: 모델 로더 인스턴스
        
    Returns:
        Optional[int]: 추천된 아이템 ID (없으면 None)
    """
    if not available_items:
        return None
    
    # 각 아이템의 벡터 계산
    item_vectors = []
    for item in available_items:
        feature = item.get('feature', '')
        if not feature:
            continue
        
        try:
            vector = item_to_vector(feature, model_loader)
            item_vectors.append({
                'id': item.get('id'),
                'vector': vector,
                'feature': feature
            })
        except Exception as e:
            print(f"⚠️ 벡터 변환 실패 (item_id={item.get('id')}): {e}")
            continue
    
    if not item_vectors:
        return None
    
    # merged_df에서 해당 카테고리가 포함된 코디 찾기
    category_kr = {'top': '상의', 'bottom': '하의', 'shoes': '신발', 'outer': '아우터'}.get(category, '')
    
    if category_kr:
        # 해당 카테고리가 포함된 코디만 필터링
        filtered_df = merged_df[
            merged_df['w2v_sentence'].str.contains(category_kr, na=False)
        ]
    else:
        filtered_df = merged_df
    
    if len(filtered_df) == 0:
        # 필터링된 코디가 없으면 전체에서 찾기
        filtered_df = merged_df
    
    # 각 아이템과 코디의 유사도 계산
    best_item = None
    best_score = -1
    
    for item_info in item_vectors:
        item_vector = item_info['vector']
        
        # 코디 벡터들과의 유사도 계산
        coord_vectors = np.array(filtered_df['final_vector'].tolist())
        similarities = cosine_similarity([item_vector], coord_vectors)[0]
        
        # 타겟 벡터와의 유사도도 고려
        target_sim = cosine_similarity([item_vector], [target_vector])[0][0]
        
        # 종합 점수 (코디 유사도 평균 + 타겟 유사도)
        coord_avg_sim = np.mean(similarities) if len(similarities) > 0 else 0
        combined_score = (coord_avg_sim * 0.7) + (target_sim * 0.3)
        
        if combined_score > best_score:
            best_score = combined_score
            best_item = item_info
    
    return best_item['id'] if best_item else None


def recommend_outfit(
    selected_items: Dict[str, Optional[Dict[str, Any]]],
    available_items: Dict[str, List[Dict[str, Any]]],
    model_loader: ModelLoader
) -> Dict[str, Any]:
    """
    코디를 추천합니다.
    
    Args:
        selected_items: 이미 선택된 아이템
            예: {"top": {"id": 1, "feature": "..."}, "bottom": None, ...}
        available_items: 선택 가능한 아이템
            예: {"bottom": [{"id": 2, "feature": "..."}, ...], ...}
        model_loader: 모델 로더 인스턴스
        
    Returns:
        Dict: 추천 결과
            예: {"recommended_outfit": {"top": 1, "bottom": 2, "shoes": 4, "outer": 5}}
    """
    if not model_loader.is_loaded():
        raise RuntimeError("모델이 로드되지 않았습니다.")
    
    # 선택된 아이템들의 feature를 벡터로 변환
    selected_features = []
    selected_categories = []
    
    for category, item in selected_items.items():
        if item is not None:
            feature = item.get('feature', '')
            if feature:
                selected_features.append(feature)
                selected_categories.append(category_mapping(category))
    
    # 타겟 벡터 생성 (선택된 아이템들의 평균 벡터)
    if selected_features:
        target_vectors = [item_to_vector(f, model_loader) for f in selected_features]
        target_vector = np.mean(target_vectors, axis=0)
    else:
        # 선택된 아이템이 없으면 merged_df의 평균 벡터 사용
        merged_df = model_loader.get_merged_df()
        if merged_df is not None and len(merged_df) > 0:
            all_vectors = np.array(merged_df['final_vector'].tolist())
            target_vector = np.mean(all_vectors, axis=0)
        else:
            raise ValueError("선택된 아이템이 없고 merged_df도 비어있습니다.")
    
    # merged_df 가져오기
    merged_df = model_loader.get_merged_df()
    if merged_df is None or len(merged_df) == 0:
        raise ValueError("merged_df가 비어있습니다.")
    
    # 추천 결과 생성
    recommended_outfit: Dict[str, Optional[int]] = {}
    
    categories = ['top', 'bottom', 'shoes', 'outer']
    
    for category in categories:
        # 이미 선택된 카테고리는 그대로 사용
        if category in selected_items and selected_items[category] is not None:
            recommended_outfit[category] = selected_items[category].get('id')
        else:
            # 추천 필요
            available = available_items.get(category, [])
            if available:
                recommended_id = recommend_category(
                    category=category,
                    available_items=available,
                    target_vector=target_vector,
                    merged_df=merged_df,
                    model_loader=model_loader
                )
                recommended_outfit[category] = recommended_id
            else:
                recommended_outfit[category] = None
    
    # 필수 카테고리 확인 (top, bottom, shoes는 필수)
    required_categories = ['top', 'bottom', 'shoes']
    for category in required_categories:
        if recommended_outfit.get(category) is None:
            raise ValueError(f"필수 카테고리 '{category}'에 대한 추천이 실패했습니다.")
    
    return {
        "recommended_outfit": recommended_outfit
    }

