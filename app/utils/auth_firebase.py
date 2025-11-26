"""
Firebase 인증 미들웨어 모듈
"""

from fastapi import Header
from typing import Optional, Dict
from ..core.firebase import verify_firebase_token
from ..core.exceptions import UnauthorizedException


def verify_firebase_auth(authorization: Optional[str] = Header(None)) -> Dict[str, str]:
    """
    Firebase 인증 토큰 검증 의존성 함수
    
    Authorization 헤더에서 Bearer 토큰을 추출하고 Firebase ID 토큰을 검증합니다.
    
    Args:
        authorization: Authorization 헤더 값 (형식: "Bearer <firebase_id_token>")
    
    Returns:
        dict: 검증된 사용자 정보
            - "firebase_uid": Firebase 사용자 UID
            - "email": 사용자 이메일
    
    Raises:
        UnauthorizedException: 토큰이 제공되지 않았거나 유효하지 않은 경우
    """
    if not authorization:
        raise UnauthorizedException(
            message="인증 토큰이 제공되지 않았습니다.",
            detail={"header": "Authorization"}
        )
    
    # "Bearer <token>" 형식에서 토큰 추출
    # "Bearer "로 시작하면 제거, 아니면 그대로 사용
    if authorization.startswith("Bearer "):
        id_token = authorization[7:].strip()  # "Bearer " (7자) 제거
    else:
        id_token = authorization.strip()
    
    if not id_token:
        raise UnauthorizedException(
            message="인증 토큰이 제공되지 않았습니다.",
            detail={"header": "Authorization", "error": "Empty token"}
        )
    
    # Firebase 토큰 검증
    try:
        token_info = verify_firebase_token(id_token)
        return token_info
    except UnauthorizedException:
        # verify_firebase_token에서 이미 UnauthorizedException을 발생시킴
        raise
    except Exception as e:
        # 예상치 못한 오류
        raise UnauthorizedException(
            message="토큰 검증 중 오류가 발생했습니다.",
            detail={"error": str(e)}
        )

