"""
즐겨찾는 코디 서비스
- 즐겨찾기 CRUD 로직
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.favorite_outfit import FavoriteOutfit
from ..models.today_outfit import TodayOutfit
from ..core.exceptions import NotFoundException, BadRequestException, ConflictException
from ..services.outfit_service import get_today_outfit


def get_favorite_list(db: Session, user_id: int) -> List[FavoriteOutfit]:
    """
    즐겨찾는 코디 목록 조회
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
    
    Returns:
        List[FavoriteOutfit]: 즐겨찾는 코디 목록
    """
    favorites = db.query(FavoriteOutfit).filter(
        FavoriteOutfit.user_id == user_id
    ).order_by(FavoriteOutfit.created_at.desc()).all()
    
    return favorites


def get_favorite_detail(db: Session, user_id: int, favorite_id: int) -> FavoriteOutfit:
    """
    특정 즐겨찾는 코디 조회
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
        favorite_id: 즐겨찾는 코디 ID
    
    Returns:
        FavoriteOutfit: 즐겨찾는 코디 객체
    
    Raises:
        NotFoundException: 즐겨찾는 코디를 찾을 수 없는 경우
    """
    favorite = db.query(FavoriteOutfit).filter(
        FavoriteOutfit.id == favorite_id,
        FavoriteOutfit.user_id == user_id
    ).first()
    
    if not favorite:
        raise NotFoundException(
            message="즐겨찾는 코디를 찾을 수 없습니다.",
            detail={"resource": "favorite_outfit", "id": favorite_id}
        )
    
    return favorite


def create_favorite_from_today_outfit(
    db: Session,
    user_id: int,
    name: str
) -> FavoriteOutfit:
    """
    오늘의 코디를 즐겨찾는 코디로 저장
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
        name: 즐겨찾는 코디 이름
    
    Returns:
        FavoriteOutfit: 생성된 즐겨찾는 코디 객체
    
    Raises:
        BadRequestException: 코디가 완성되지 않은 경우
        ConflictException: 같은 이름의 즐겨찾기가 이미 있는 경우
    """
    # 오늘의 코디 조회
    today_outfit = get_today_outfit(db, user_id)
    
    # 코디가 완성되었는지 확인 (필수 카테고리만 선택되어 있어야 함)
    # outer는 선택 사항이므로 필수 카테고리(top, bottom, shoes)만 확인
    if not all([
        today_outfit.top_id,
        today_outfit.bottom_id,
        today_outfit.shoes_id
    ]):
        raise BadRequestException(
            message="코디를 완성해주세요. (top, bottom, shoes가 모두 선택되어야 합니다)",
            detail={"today_outfit": {
                "top_id": today_outfit.top_id,
                "bottom_id": today_outfit.bottom_id,
                "shoes_id": today_outfit.shoes_id,
                "outer_id": today_outfit.outer_id  # outer는 선택 사항이지만 정보 제공
            }}
        )
    
    # 같은 이름의 즐겨찾기가 이미 있는지 확인
    existing = db.query(FavoriteOutfit).filter(
        FavoriteOutfit.user_id == user_id,
        FavoriteOutfit.name == name
    ).first()
    
    if existing:
        raise ConflictException(
            message="이미 같은 이름의 즐겨찾는 코디가 있습니다.",
            detail={"name": name}
        )
    
    # 같은 조합의 코디가 이미 있는지 확인
    existing_combination = db.query(FavoriteOutfit).filter(
        FavoriteOutfit.user_id == user_id,
        FavoriteOutfit.top_id == today_outfit.top_id,
        FavoriteOutfit.bottom_id == today_outfit.bottom_id,
        FavoriteOutfit.shoes_id == today_outfit.shoes_id,
        FavoriteOutfit.outer_id == today_outfit.outer_id
    ).first()
    
    if existing_combination:
        raise ConflictException(
            message=f"이미 저장된 코디입니다 - {existing_combination.name}",
            detail={"existing_name": existing_combination.name}
        )
    
    # 즐겨찾는 코디 생성
    favorite = FavoriteOutfit(
        user_id=user_id,
        name=name,
        top_id=today_outfit.top_id,
        bottom_id=today_outfit.bottom_id,
        shoes_id=today_outfit.shoes_id,
        outer_id=today_outfit.outer_id,
        created_at=datetime.utcnow()
    )
    
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    # 오늘의 코디 초기화 (저장 후 초기화)
    today_outfit.top_id = None
    today_outfit.bottom_id = None
    today_outfit.shoes_id = None
    today_outfit.outer_id = None
    today_outfit.updated_at = datetime.utcnow()
    
    db.commit()
    
    return favorite


def update_favorite_name(
    db: Session,
    user_id: int,
    favorite_id: int,
    new_name: str
) -> FavoriteOutfit:
    """
    즐겨찾는 코디 이름 변경
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
        favorite_id: 즐겨찾는 코디 ID
        new_name: 새로운 이름
    
    Returns:
        FavoriteOutfit: 업데이트된 즐겨찾는 코디 객체
    
    Raises:
        NotFoundException: 즐겨찾는 코디를 찾을 수 없는 경우
        ConflictException: 같은 이름의 즐겨찾기가 이미 있는 경우
    """
    favorite = get_favorite_detail(db, user_id, favorite_id)
    
    # 같은 이름의 즐겨찾기가 이미 있는지 확인 (현재 항목 제외)
    existing = db.query(FavoriteOutfit).filter(
        FavoriteOutfit.user_id == user_id,
        FavoriteOutfit.name == new_name,
        FavoriteOutfit.id != favorite_id
    ).first()
    
    if existing:
        raise ConflictException(
            message="이미 같은 이름의 즐겨찾는 코디가 있습니다.",
            detail={"name": new_name}
        )
    
    favorite.name = new_name
    db.commit()
    db.refresh(favorite)
    
    return favorite


def delete_favorite(
    db: Session,
    user_id: int,
    favorite_id: int
) -> None:
    """
    즐겨찾는 코디 삭제
    
    Args:
        db: DB 세션
        user_id: 사용자 ID
        favorite_id: 즐겨찾는 코디 ID
    
    Raises:
        NotFoundException: 즐겨찾는 코디를 찾을 수 없는 경우
    """
    favorite = get_favorite_detail(db, user_id, favorite_id)
    
    db.delete(favorite)
    db.commit()

