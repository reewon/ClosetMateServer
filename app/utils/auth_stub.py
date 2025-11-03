from fastapi import Header, HTTPException, status
from typing import Optional
from ..core.exceptions import UnauthorizedException


# 테스트용 고정 토큰
TEST_TOKEN = "test-token"
TEST_USER_ID = 1
TEST_USERNAME = "test_user"


def verify_test_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    테스트용 토큰 검증 함수
    
    Args:
        authorization: Authorization 헤더 값 (형식: "test-token")
    
    Returns:
        dict: 사용자 정보 {"user_id": 1, "username": "test_user"}
    
    Raises:
        UnauthorizedException: 토큰이 유효하지 않은 경우
    """
    if not authorization:
        raise UnauthorizedException(
            message="인증 토큰이 제공되지 않았습니다.",
            detail={"header": "Authorization"}
        )
    
    # "Bearer test-token" 또는 "test-token" 형식 모두 지원
    token = authorization.replace("Bearer ", "").strip()
    
    if token != TEST_TOKEN:
        raise UnauthorizedException(
            message="유효하지 않은 인증 토큰입니다.",
            detail={"token": token}
        )
    
    return {
        "user_id": TEST_USER_ID,
        "username": TEST_USERNAME
    }

