"""
오늘의 코디 라우터
- 코디 조회, 업데이트, 초기화, AI 추천
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..utils.dependencies import get_current_user, get_db
from ..models.user import User
from ..models.closet_item import ClosetItem
from ..schemas.outfit_schema import (
    TodayOutfitResponse,
    OutfitUpdateRequest,
    OutfitClearRequest,
    OutfitRecommendResponse,
    ItemInfo
)
from ..schemas.closet_schema import MessageResponse
from ..services.outfit_service import (
    get_today_outfit,
    update_outfit_item,
    clear_outfit_category
)
from ..services.ai_service import recommend_outfit
from ..core.exceptions import NotFoundException

router = APIRouter(prefix="/outfit", tags=["Outfit"])


def _convert_to_today_outfit_response(today_outfit, db: Session) -> TodayOutfitResponse:
    """
    TodayOutfit 객체를 TodayOutfitResponse로 변환(API 응답 시 아이템 명을 가져오기 위함)
    
    Args:
        today_outfit: TodayOutfit 객체
        db: DB 세션
    
    Returns:
        TodayOutfitResponse: 응답 스키마
    """
    response_data = {}
    categories = ["top", "bottom", "shoes", "outer"]
    
    for category in categories:
        item_id = getattr(today_outfit, f"{category}_id")
        if item_id:
            item = db.query(ClosetItem).filter(ClosetItem.id == item_id).first()
            if item:
                response_data[category] = ItemInfo(id=item.id, name=item.name)
            else:
                response_data[category] = None
        else:
            response_data[category] = None
    
    return TodayOutfitResponse(**response_data)


@router.get("/today", response_model=TodayOutfitResponse)
def get_today_outfit_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    오늘의 코디 보기
    
    Args:
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        TodayOutfitResponse: 오늘의 코디 정보
    """
    today_outfit = get_today_outfit(db, current_user.id)
    return _convert_to_today_outfit_response(today_outfit, db)


@router.put("/today", response_model=MessageResponse)
def update_outfit_item_endpoint(
    request: OutfitUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    코디 아이템 선택/변경
    
    Args:
        request: 업데이트 요청 데이터
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        MessageResponse: 변경 완료 메시지
    """
    update_outfit_item(db, current_user.id, request.category, request.item_id)
    
    return MessageResponse(message=f"{request.category} 변경 완료")


@router.put("/clear", response_model=MessageResponse)
def clear_outfit_category_endpoint(
    request: OutfitClearRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 카테고리 비우기
    
    Args:
        request: 비우기 요청 데이터
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        MessageResponse: 비워짐 완료 메시지
    """
    clear_outfit_category(db, current_user.id, request.category)
    
    return MessageResponse(message=f"{request.category} 비우기 완료")


@router.post("/recommend", response_model=OutfitRecommendResponse)
def recommend_outfit_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI 추천 실행 (현재는 랜덤 추천)
    
    Args:
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        OutfitRecommendResponse: 추천된 코디 정보
    """
    # 현재 오늘의 코디 가져오기
    today_outfit = get_today_outfit(db, current_user.id)
    
    # 이미 선택된 아이템 추출
    existing_items = {}
    if today_outfit.top_id:
        existing_items["top"] = today_outfit.top_id
    if today_outfit.bottom_id:
        existing_items["bottom"] = today_outfit.bottom_id
    if today_outfit.shoes_id:
        existing_items["shoes"] = today_outfit.shoes_id
    if today_outfit.outer_id:
        existing_items["outer"] = today_outfit.outer_id
    
    # AI 추천 실행 (현재는 랜덤)
    recommended_ids = recommend_outfit(db, current_user.id, existing_items)
    
    # 추천 결과를 오늘의 코디에 반영
    today_outfit.top_id = recommended_ids.get("top")
    today_outfit.bottom_id = recommended_ids.get("bottom")
    today_outfit.shoes_id = recommended_ids.get("shoes")
    today_outfit.outer_id = recommended_ids.get("outer")
    
    db.commit()
    db.refresh(today_outfit)
    
    # 응답 형식으로 변환
    response_data = {}
    categories = ["top", "bottom", "shoes", "outer"]
    
    for category in categories:
        item_id = recommended_ids.get(category)
        if item_id:
            item = db.query(ClosetItem).filter(ClosetItem.id == item_id).first()
            if item:
                response_data[category] = ItemInfo(id=item.id, name=item.name)
            else:
                response_data[category] = None
        else:
            response_data[category] = None
    
    return OutfitRecommendResponse(**response_data)

