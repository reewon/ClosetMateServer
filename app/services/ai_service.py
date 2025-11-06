"""
AI 추천 서비스 (랜덤 추천)
- 사용자 옷장에서 랜덤으로 코디 추천
"""

import random
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from ..models.closet_item import ClosetItem
from ..core.exceptions import NotFoundException, BadRequestException


def recommend_outfit(
    db: Session,
    user_id: int,
    existing_items: Optional[Dict[str, int]] = None
) -> Dict[str, Optional[int]]:
    """
    사용자 옷장에서 랜덤으로 코디를 추천하는 함수
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
        existing_items: 이미 선택된 아이템 (예: {"bottom": 2})
    
    Returns:
        Dict[str, Optional[int]]: 추천된 아이템 ID 딕셔너리
        예: {"top": 1, "bottom": 2, "shoes": 3, "outer": 4}
    
    Raises:
        NotFoundException: 옷장에 아이템이 없는 경우
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
    
    # 카테고리별로 아이템 분류
    items_by_category: Dict[str, List[ClosetItem]] = {
        "top": [],
        "bottom": [],
        "shoes": [],
        "outer": []
    }
    
    for item in user_items:
        if item.category in items_by_category:
            items_by_category[item.category].append(item)
    
    # 추천 결과 생성
    recommended: Dict[str, Optional[int]] = {}
    categories = ["top", "bottom", "shoes", "outer"]
    
    for category in categories:
        if category in existing_items:
            # 이미 선택된 카테고리는 그대로 사용
            recommended[category] = existing_items[category]
        else:
            # 랜덤으로 선택
            category_items = items_by_category.get(category, [])
            recommended[category] = random.choice(category_items).id if category_items else None
    
    return recommended

