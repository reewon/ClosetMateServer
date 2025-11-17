from pydantic import BaseModel
from typing import Optional


class ClosetItemResponse(BaseModel):
    """옷장 아이템 응답 스키마"""
    id: int
    feature: str  # Gemini API로 추출한 피쳐 정보 (항상 값 있음)
    image_url: str  # 이미지 URL (항상 값 있음)

    class Config:
        from_attributes = True


class ClosetItemCreate(BaseModel):
    """옷장 아이템 생성 요청 스키마
    
    주의: 실제로는 라우터에서 UploadFile로 이미지를 직접 받습니다.
    이 스키마는 현재 사용되지 않지만, 향후 확장을 위해 유지합니다.
    """
    pass  # 이미지에서 feature를 추출하므로 별도 필드 불필요


class MessageResponse(BaseModel):
    """일반 메시지 응답 스키마"""
    message: str

