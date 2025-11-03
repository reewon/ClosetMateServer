"""
인증 라우터 (테스트용)
"""

from fastapi import APIRouter
from ..schemas.user_schema import TokenResponse
from ..utils.auth_stub import TEST_TOKEN

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/test-login", response_model=TokenResponse)
def test_login():
    """
    테스트용 토큰 발급
    
    Returns:
        TokenResponse: 테스트 토큰
    """
    return TokenResponse(token=TEST_TOKEN)

