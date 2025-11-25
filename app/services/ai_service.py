"""
AI 추천 서비스
- ai_recommendation 모듈을 사용하여 코디 추천
"""

from typing import Dict, Optional, List, Any
from sqlalchemy.orm import Session
from ..models.closet_item import ClosetItem
from ..core.exceptions import NotFoundException, BadRequestException

# AI 추천 모듈 import
try:
    from ai_recommendation.model_loader import get_model_loader
    from ai_recommendation.recommendation_engine import recommend_outfit as ai_recommend_outfit
    AI_RECOMMENDATION_AVAILABLE = True
except ImportError:
    AI_RECOMMENDATION_AVAILABLE = False
    print("⚠️ ai_recommendation 모듈을 찾을 수 없습니다.")


def recommend_outfit(
    db: Session,
    user_id: int,
    existing_items: Optional[Dict[str, int]] = None
) -> Dict[str, Optional[int]]:
    """
    AI 추천 모델을 사용하여 코디를 추천하는 함수
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
        existing_items: 이미 선택된 아이템 (예: {"bottom": 2})
    
    Returns:
        Dict[str, Optional[int]]: 추천된 아이템 ID 딕셔너리
        예: {"top": 1, "bottom": 2, "shoes": 3, "outer": 4}
    
    Raises:
        NotFoundException: 옷장에 아이템이 없는 경우
        BadRequestException: AI 추천 모델이 로드되지 않았거나 추천 실패 시
    """
    if existing_items is None:
        existing_items = {}
    
    # 사용자의 옷장에서 아이템 조회
    user_items = db.query(ClosetItem).filter(
        ClosetItem.user_id == user_id
    ).all()
    
    if not user_items:
        raise NotFoundException(
            message="옷장에 아이템이 없습니다.",
            detail={"resource": "closet_items", "user_id": user_id}
        )
    
    # AI 추천 모델 사용 가능 여부 확인
    if not AI_RECOMMENDATION_AVAILABLE:
        raise BadRequestException(
            message="AI 추천 모델을 사용할 수 없습니다. ai_recommendation 모듈이 설치되지 않았습니다.",
            detail={"error": "AI_RECOMMENDATION_AVAILABLE is False"}
        )
    
    # 모델 로더 가져오기
    try:
        model_loader = get_model_loader()
    except Exception as e:
        raise BadRequestException(
            message="AI 추천 모델을 로드할 수 없습니다.",
            detail={"error": str(e)}
        )
    
    # 카테고리별로 아이템 분류 및 feature 정보 포함
    items_by_category: Dict[str, List[ClosetItem]] = {
        "top": [],
        "bottom": [],
        "shoes": [],
        "outer": []
    }
    
    for item in user_items:
        if item.category in items_by_category:
            items_by_category[item.category].append(item)
    
    # selected_items 형식으로 변환 (이미 선택된 아이템)
    selected_items: Dict[str, Optional[Dict[str, Any]]] = {
        "top": None,
        "bottom": None,
        "shoes": None,
        "outer": None
    }
    
    for category, item_id in existing_items.items():
        if item_id and category in items_by_category:
            # 해당 아이템 찾기
            item = next((i for i in items_by_category[category] if i.id == item_id), None)
            if item and item.feature:
                selected_items[category] = {
                    "id": item.id,
                    "feature": item.feature
                }
    
    # available_items 형식으로 변환 (선택 가능한 아이템)
    available_items: Dict[str, List[Dict[str, Any]]] = {
        "top": [],
        "bottom": [],
        "shoes": [],
        "outer": []
    }
    
    for category in ["top", "bottom", "shoes", "outer"]:
        # 이미 선택된 카테고리는 available_items에 포함하지 않음
        if category not in existing_items or existing_items[category] is None:
            for item in items_by_category.get(category, []):
                if item.feature:  # feature가 있는 아이템만 포함
                    available_items[category].append({
                        "id": item.id,
                        "feature": item.feature
                    })
    
    # AI 추천 실행
    try:
        result = ai_recommend_outfit(
            selected_items=selected_items,
            available_items=available_items,
            model_loader=model_loader
        )
        
        # 추천 결과 추출
        recommended_outfit = result.get("recommended_outfit", {})
        
        # 반환 형식 변환
        recommended: Dict[str, Optional[int]] = {
            "top": recommended_outfit.get("top"),
            "bottom": recommended_outfit.get("bottom"),
            "shoes": recommended_outfit.get("shoes"),
            "outer": recommended_outfit.get("outer")
        }
        
        return recommended
        
    except Exception as e:
        raise BadRequestException(
            message="AI 추천 중 오류가 발생했습니다.",
            detail={"error": str(e)}
        )

