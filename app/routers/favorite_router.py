"""
즐겨찾는 코디 라우터
- 즐겨찾는 코디 CRUD
"""

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from typing import List
from ..utils.dependencies import get_current_user, get_db
from ..models.user import User
from ..models.closet_item import ClosetItem
from ..schemas.favorite_schema import (
    FavoriteOutfitListItem,
    FavoriteOutfitDetail,
    FavoriteOutfitCreate,
    FavoriteOutfitUpdate
)
from ..schemas.outfit_schema import ItemInfo
from ..schemas.closet_schema import MessageResponse
from ..services.favorite_service import (
    get_favorite_list,
    get_favorite_detail,
    create_favorite_from_today_outfit,
    update_favorite_name,
    delete_favorite
)

router = APIRouter(prefix="/favorites", tags=["Favorites"])


def _convert_to_favorite_detail(favorite, db: Session) -> FavoriteOutfitDetail:
    """
    FavoriteOutfit 객체를 FavoriteOutfitDetail로 변환(API 응답 시 아이템 명을 가져오기 위함)
    
    Args:
        favorite: FavoriteOutfit 객체
        db: DB 세션
    
    Returns:
        FavoriteOutfitDetail: 응답 스키마
    """
    response_data = {"name": favorite.name}
    categories = ["상의", "하의", "신발", "아우터"]
    
    for category in categories:
        item_id = getattr(favorite, f"{category}_id")
        if item_id:
            item = db.query(ClosetItem).filter(ClosetItem.id == item_id).first()
            if item:
                response_data[category] = ItemInfo(id=item.id, name=item.name)
            else:
                response_data[category] = None
        else:
            response_data[category] = None
    
    return FavoriteOutfitDetail(**response_data)


@router.get("", response_model=List[FavoriteOutfitListItem])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    즐겨찾는 코디 목록 조회
    
    Args:
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        List[FavoriteOutfitListItem]: 즐겨찾는 코디 목록
    """
    favorites = get_favorite_list(db, current_user.id)
    return [
        FavoriteOutfitListItem(id=fav.id, name=fav.name) for fav in favorites
    ]


@router.get("/{id}", response_model=FavoriteOutfitDetail)
def get_favorite(
    id: int = Path(..., description="즐겨찾는 코디 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 코디 보기
    
    Args:
        id: 즐겨찾는 코디 ID
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        FavoriteOutfitDetail: 즐겨찾는 코디 상세 정보
    """
    favorite = get_favorite_detail(db, current_user.id, id)
    return _convert_to_favorite_detail(favorite, db)


@router.post("", response_model=MessageResponse)
def create_favorite(
    request: FavoriteOutfitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    오늘의 코디 즐겨찾기 저장
    
    Args:
        request: 즐겨찾기 생성 요청 데이터
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        MessageResponse: 저장 완료 메시지
    """
    create_favorite_from_today_outfit(db, current_user.id, request.name)
    return MessageResponse(message="저장 완료")


@router.put("/{id}", response_model=MessageResponse)
def update_favorite_name(
    id: int = Path(..., description="즐겨찾는 코디 ID"),
    request: FavoriteOutfitUpdate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    코디 이름 변경
    
    Args:
        id: 즐겨찾는 코디 ID
        request: 이름 변경 요청 데이터
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        MessageResponse: 이름 변경 완료 메시지
    """
    update_favorite_name(db, current_user.id, id, request.new_name)
    return MessageResponse(message="이름이 변경되었습니다.")


@router.delete("/{id}", response_model=MessageResponse)
def delete_favorite_endpoint(
    id: int = Path(..., description="즐겨찾는 코디 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    코디 삭제
    
    Args:
        id: 즐겨찾는 코디 ID
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        MessageResponse: 삭제 완료 메시지
    """
    delete_favorite(db, current_user.id, id)
    return MessageResponse(message="삭제 완료")

