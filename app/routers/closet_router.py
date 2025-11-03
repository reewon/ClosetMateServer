"""
옷장 라우터
- 옷장 아이템 CRUD
"""

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from typing import List
from ..utils.dependencies import get_current_user, get_db
from ..models.user import User
from ..models.closet_item import ClosetItem
from ..schemas.closet_schema import (
    ClosetItemResponse,
    ClosetItemCreate,
    MessageResponse
)
from ..core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/closet", tags=["Closet"])


@router.get("/{category}", response_model=List[ClosetItemResponse])
def get_closet_items(
    category: str = Path(..., description="카테고리 (상의, 하의, 신발, 아우터)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    카테고리별 옷 조회
    
    Args:
        category: 카테고리
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        List[ClosetItemResponse]: 옷장 아이템 목록
    
    Raises:
        BadRequestException: 잘못된 카테고리인 경우
    """
    valid_categories = ["상의", "하의", "신발", "아우터"]
    if category not in valid_categories:
        raise BadRequestException(
            message=f"잘못된 카테고리입니다. 가능한 값: {', '.join(valid_categories)}",
            detail={"category": category}
        )
    
    items = db.query(ClosetItem).filter(
        ClosetItem.user_id == current_user.id,
        ClosetItem.category == category
    ).all()
    
    return [ClosetItemResponse(id=item.id, name=item.name) for item in items]


@router.post("/{category}", response_model=MessageResponse)
def create_closet_item(
    category: str = Path(..., description="카테고리 (상의, 하의, 신발, 아우터)"),
    item_data: ClosetItemCreate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    옷 추가
    
    Args:
        category: 카테고리
        item_data: 아이템 데이터
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        MessageResponse: 추가 완료 메시지
    
    Raises:
        BadRequestException: 잘못된 카테고리인 경우
    """
    valid_categories = ["상의", "하의", "신발", "아우터"]
    if category not in valid_categories:
        raise BadRequestException(
            message=f"잘못된 카테고리입니다. 가능한 값: {', '.join(valid_categories)}",
            detail={"category": category}
        )
    
    new_item = ClosetItem(
        user_id=current_user.id,
        category=category,
        name=item_data.name,
        image_url=None  # CLI 기반이므로 이미지 없음
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return MessageResponse(message="추가 완료")


@router.delete("/{item_id}", response_model=MessageResponse)
def delete_closet_item(
    item_id: int = Path(..., description="아이템 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    옷 삭제
    
    Args:
        item_id: 아이템 ID
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        MessageResponse: 삭제 완료 메시지
    
    Raises:
        NotFoundException: 아이템을 찾을 수 없는 경우
    """
    item = db.query(ClosetItem).filter(
        ClosetItem.id == item_id,
        ClosetItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise NotFoundException(
            message="옷장 아이템을 찾을 수 없습니다.",
            detail={"resource": "closet_item", "id": item_id}
        )
    
    db.delete(item)
    db.commit()
    
    return MessageResponse(message="삭제 완료")

