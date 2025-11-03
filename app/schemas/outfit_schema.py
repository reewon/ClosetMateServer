from pydantic import BaseModel
from typing import Optional


class ItemInfo(BaseModel):
    """코디 아이템 정보 스키마 (id, name 포함)"""
    id: int
    name: str

    class Config:
        from_attributes = True


class TodayOutfitResponse(BaseModel):
    """오늘의 코디 응답 스키마"""
    상의: Optional[ItemInfo] = None
    하의: Optional[ItemInfo] = None
    신발: Optional[ItemInfo] = None
    아우터: Optional[ItemInfo] = None

    class Config:
        from_attributes = True


class OutfitUpdateRequest(BaseModel):
    """코디 아이템 선택/변경 요청 스키마"""
    category: str  # 상의, 하의, 신발, 아우터
    item_id: int


class OutfitClearRequest(BaseModel):
    """코디 카테고리 비우기 요청 스키마"""
    category: str  # 상의, 하의, 신발, 아우터


class OutfitRecommendResponse(BaseModel):
    """AI 추천 코디 응답 스키마"""
    상의: Optional[ItemInfo] = None
    하의: Optional[ItemInfo] = None
    신발: Optional[ItemInfo] = None
    아우터: Optional[ItemInfo] = None

    class Config:
        from_attributes = True

