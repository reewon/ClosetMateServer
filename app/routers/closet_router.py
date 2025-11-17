"""
옷장 라우터
- 옷장 아이템 CRUD
"""

from fastapi import APIRouter, Depends, Path, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from ..utils.dependencies import get_current_user, get_db
from ..models.user import User
from ..models.closet_item import ClosetItem
from ..schemas.closet_schema import (
    ClosetItemResponse,
    # ClosetItemCreate,  # 혹시 모를 사용 가능성을 위해 주석 처리하여 유지
    MessageResponse
)
from ..services import (
    analyze_clothing_image_from_bytes,
    save_image,
    delete_image
)
from ..core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/closet", tags=["Closet"])


@router.get("/{category}", response_model=List[ClosetItemResponse])
def get_closet_items(
    category: str = Path(..., description="카테고리 (top, bottom, shoes, outer)"),
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
    valid_categories = ["top", "bottom", "shoes", "outer"]
    if category not in valid_categories:
        raise BadRequestException(
            message=f"잘못된 카테고리입니다. 가능한 값: {', '.join(valid_categories)}",
            detail={"category": category}
        )
    
    # feature와 image_url이 모두 있는 완전한 아이템만 조회
    # (불완전한 데이터는 제외)
    items = db.query(ClosetItem).filter(
        ClosetItem.user_id == current_user.id,
        ClosetItem.category == category,
        ClosetItem.feature.isnot(None),
        ClosetItem.image_url.isnot(None)
    ).all()
    
    return [
        ClosetItemResponse(
            id=item.id,
            feature=item.feature,
            image_url=item.image_url
        ) for item in items
    ]


@router.post("/{category}", response_model=MessageResponse)
async def create_closet_item(
    category: str = Path(..., description="카테고리 (top, bottom, shoes, outer)"),
    image: UploadFile = File(..., description="옷 이미지 파일"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    옷 추가 (이미지 업로드 및 Gemini API로 feature 추출)
    
    Args:
        category: 카테고리 (top, bottom, shoes, outer)
        image: 업로드된 이미지 파일
        current_user: 현재 사용자
        db: DB 세션
    
    Returns:
        MessageResponse: 추가 완료 메시지
    
    Raises:
        BadRequestException: 잘못된 카테고리 또는 이미지 처리 실패 시
    """
    # 카테고리 검증
    valid_categories = ["top", "bottom", "shoes", "outer"]
    if category not in valid_categories:
        raise BadRequestException(
            message=f"잘못된 카테고리입니다. 가능한 값: {', '.join(valid_categories)}",
            detail={"category": category}
        )
    
    # 이미지 파일 검증
    if not image.content_type or not image.content_type.startswith("image/"):
        raise BadRequestException(
            message="이미지 파일만 업로드 가능합니다.",
            detail={"content_type": image.content_type}
        )
    
    try:
        # 이미지 바이너리 데이터 읽기
        image_bytes = await image.read()
        
        if len(image_bytes) == 0:
            raise BadRequestException(
                message="이미지 파일이 비어있습니다.",
                detail={}
            )
        
        # 파일 확장자 추출
        filename = image.filename or "image"
        file_extension = filename.split(".")[-1].lower() if "." in filename else "jpg"
        
        # 사용자 성별 가져오기
        user_gender = current_user.gender
        
        # 1. Gemini API로 feature 추출
        feature = analyze_clothing_image_from_bytes(
            image_bytes=image_bytes,
            category=category,
            user_gender=user_gender
        )
        
        # 2. DB에 아이템 생성 (이미지 저장 전에 ID를 얻기 위해)
        new_item = ClosetItem(
            user_id=current_user.id,
            category=category,
            feature=feature,
            image_url=None  # 아직 저장 전
        )
        
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        # 3. 이미지 저장
        image_url = save_image(
            image_bytes=image_bytes,
            user_id=current_user.id,
            item_id=new_item.id,
            file_extension=file_extension
        )
        
        # 4. image_url 업데이트
        new_item.image_url = image_url
        db.commit()
        
        return MessageResponse(message="추가 완료")
        
    except BadRequestException:
        # BadRequestException은 그대로 전달
        raise
    except Exception as e:
        # 예상치 못한 오류 처리
        raise BadRequestException(
            message=f"옷 추가 중 오류가 발생했습니다: {str(e)}",
            detail={"error": str(e)}
        )


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
    
    # 이미지 파일 삭제 (있는 경우)
    if item.image_url:
        try:
            delete_image(item.image_url)
        except Exception as e:
            # 이미지 삭제 실패는 로그만 남기고 계속 진행
            print(f"이미지 삭제 실패 (계속 진행): {item.image_url}, 오류: {str(e)}")
    
    db.delete(item)
    db.commit()
    
    return MessageResponse(message="삭제 완료")

