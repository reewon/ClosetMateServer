from pydantic import BaseModel
from typing import Optional
from .outfit_schema import ItemInfo


class FavoriteOutfitListItem(BaseModel):
    """즐겨찾는 코디 목록 항목 스키마"""
    id: int
    name: str

    class Config:
        from_attributes = True


class FavoriteOutfitDetail(BaseModel):
    """즐겨찾는 코디 상세 정보 스키마"""
    name: str
    top: Optional[ItemInfo] = None
    bottom: Optional[ItemInfo] = None
    shoes: Optional[ItemInfo] = None
    outer: Optional[ItemInfo] = None

    class Config:
        from_attributes = True


class FavoriteOutfitCreate(BaseModel):
    """즐겨찾는 코디 생성 요청 스키마"""
    name: str


class FavoriteOutfitUpdate(BaseModel):
    """즐겨찾는 코디 이름 변경 요청 스키마"""
    new_name: str

