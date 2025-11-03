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
    categories = ["상의", "하의", "신발", "아우터"]
    
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
    
    category_names = {"상의": "상의", "하의": "하의", "신발": "신발", "아우터": "아우터"}
    category_name = category_names.get(request.category, request.category)
    
    return MessageResponse(message=f"{category_name}가 변경되었습니다.")


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
    
    category_names = {"상의": "상의", "하의": "하의", "신발": "신발", "아우터": "아우터"}
    category_name = category_names.get(request.category, request.category)
    
    return MessageResponse(message=f"{category_name}가 비워졌습니다.")


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
    if today_outfit.상의_id:
        existing_items["상의"] = today_outfit.상의_id
    if today_outfit.하의_id:
        existing_items["하의"] = today_outfit.하의_id
    if today_outfit.신발_id:
        existing_items["신발"] = today_outfit.신발_id
    if today_outfit.아우터_id:
        existing_items["아우터"] = today_outfit.아우터_id
    
    # AI 추천 실행 (현재는 랜덤)
    recommended_ids = recommend_outfit(db, current_user.id, existing_items)
    
    # 추천 결과를 오늘의 코디에 반영
    today_outfit.상의_id = recommended_ids.get("상의")
    today_outfit.하의_id = recommended_ids.get("하의")
    today_outfit.신발_id = recommended_ids.get("신발")
    today_outfit.아우터_id = recommended_ids.get("아우터")
    
    db.commit()
    db.refresh(today_outfit)
    
    # 응답 형식으로 변환
    response_data = {}
    categories = ["상의", "하의", "신발", "아우터"]
    
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

