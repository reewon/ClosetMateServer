from pydantic import BaseModel, Field
from typing import Optional


class TokenResponse(BaseModel):
    """테스트 토큰 응답 스키마"""
    token: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    id: int
    firebase_uid: str
    email: str
    username: str
    gender: str

    class Config:
        from_attributes = True


class UserSyncRequest(BaseModel):
    """사용자 정보 동기화 요청 스키마"""
    username: str = Field(..., min_length=1, max_length=50, description="사용자 닉네임")
    gender: str = Field(..., description="성별 (남성 또는 여성)")

    class Config:
        from_attributes = True

