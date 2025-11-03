from pydantic import BaseModel


class TokenResponse(BaseModel):
    """테스트 토큰 응답 스키마"""
    token: str

    class Config:
        from_attributes = True

