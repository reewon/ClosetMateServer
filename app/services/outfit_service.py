"""
오늘의 코디 서비스
- 코디 업데이트, 초기화, 조회 로직
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.today_outfit import TodayOutfit
from ..models.closet_item import ClosetItem
from ..core.exceptions import NotFoundException, BadRequestException


def get_today_outfit(db: Session, user_id: int) -> TodayOutfit:
    """
    오늘의 코디 조회 또는 생성
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
    
    Returns:
        TodayOutfit: 오늘의 코디 객체
    """
    today_outfit = db.query(TodayOutfit).filter(
        TodayOutfit.user_id == user_id
    ).first()
    
    # 없으면 생성
    if not today_outfit:
        today_outfit = TodayOutfit(
            user_id=user_id,
            상의_id=None,
            하의_id=None,
            신발_id=None,
            아우터_id=None,
            updated_at=datetime.utcnow()
        )
        db.add(today_outfit)
        db.commit()
        db.refresh(today_outfit)
    
    return today_outfit


def update_outfit_item(
    db: Session,
    user_id: int,
    category: str,
    item_id: int
) -> TodayOutfit:
    """
    오늘의 코디에서 특정 카테고리 아이템 선택/변경
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
        category: 카테고리 (상의, 하의, 신발, 아우터)
        item_id: 아이템 ID
    
    Returns:
        TodayOutfit: 업데이트된 오늘의 코디 객체
    
    Raises:
        BadRequestException: 잘못된 카테고리 또는 아이템이 없는 경우
    """
    valid_categories = ["상의", "하의", "신발", "아우터"]
    if category not in valid_categories:
        raise BadRequestException(
            message=f"잘못된 카테고리입니다. 가능한 값: {', '.join(valid_categories)}",
            detail={"category": category}
        )
    
    # 아이템이 사용자의 옷장에 있는지 확인
    item = db.query(ClosetItem).filter(
        ClosetItem.id == item_id,
        ClosetItem.user_id == user_id,
        ClosetItem.category == category
    ).first()
    
    if not item:
        raise NotFoundException(
            message="해당 카테고리의 아이템을 찾을 수 없습니다.",
            detail={"resource": "closet_item", "item_id": item_id, "category": category}
        )
    
    # 오늘의 코디 조회 또는 생성
    today_outfit = get_today_outfit(db, user_id)
    
    # 카테고리별 필드 업데이트
    category_field_map = {
        "상의": "상의_id",
        "하의": "하의_id",
        "신발": "신발_id",
        "아우터": "아우터_id"
    }
    
    setattr(today_outfit, category_field_map[category], item_id)
    today_outfit.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(today_outfit)
    
    return today_outfit


def clear_outfit_category(
    db: Session,
    user_id: int,
    category: str
) -> TodayOutfit:
    """
    오늘의 코디에서 특정 카테고리 비우기
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
        category: 카테고리 (상의, 하의, 신발, 아우터)
    
    Returns:
        TodayOutfit: 업데이트된 오늘의 코디 객체
    
    Raises:
        BadRequestException: 잘못된 카테고리인 경우
    """
    valid_categories = ["상의", "하의", "신발", "아우터"]
    if category not in valid_categories:
        raise BadRequestException(
            message=f"잘못된 카테고리입니다. 가능한 값: {', '.join(valid_categories)}",
            detail={"category": category}
        )
    
    # 오늘의 코디 조회 또는 생성
    today_outfit = get_today_outfit(db, user_id)
    
    # 카테고리별 필드 비우기
    category_field_map = {
        "상의": "상의_id",
        "하의": "하의_id",
        "신발": "신발_id",
        "아우터": "아우터_id"
    }
    
    setattr(today_outfit, category_field_map[category], None)
    today_outfit.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(today_outfit)
    
    return today_outfit



