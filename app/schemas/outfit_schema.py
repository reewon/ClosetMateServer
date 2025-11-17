from pydantic import BaseModel
from typing import Optional


class ItemInfo(BaseModel):
    """코디 아이템 정보 스키마 (id, image_url 포함)"""
    id: int
    image_url: Optional[str] = None  # 이미지 URL (사용자에게 표시용)

    class Config:
        from_attributes = True


class TodayOutfitResponse(BaseModel):
    """오늘의 코디 응답 스키마"""
    top: Optional[ItemInfo] = None
    bottom: Optional[ItemInfo] = None
    shoes: Optional[ItemInfo] = None
    outer: Optional[ItemInfo] = None

    class Config:
        from_attributes = True


class OutfitUpdateRequest(BaseModel):
    """코디 아이템 선택/변경 요청 스키마"""
    category: str  # top, bottom, shoes, outer
    item_id: int


class OutfitClearRequest(BaseModel):
    """코디 카테고리 비우기 요청 스키마"""
    category: str  # top, bottom, shoes, outer


class OutfitRecommendResponse(BaseModel):
    """AI 추천 코디 응답 스키마"""
    top: Optional[ItemInfo] = None
    bottom: Optional[ItemInfo] = None
    shoes: Optional[ItemInfo] = None
    outer: Optional[ItemInfo] = None

    class Config:
        from_attributes = True

