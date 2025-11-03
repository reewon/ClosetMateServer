from pydantic import BaseModel
from typing import Optional


class ClosetItemResponse(BaseModel):
    """옷장 아이템 응답 스키마"""
    id: int
    name: str

    class Config:
        from_attributes = True


class ClosetItemCreate(BaseModel):
    """옷장 아이템 생성 요청 스키마"""
    name: str


class MessageResponse(BaseModel):
    """일반 메시지 응답 스키마"""
    message: str

