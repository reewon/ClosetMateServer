"""
JWT 인증 모듈 (추후 auth_stub.py를 대체할 파일)

사용 방법:
1. auth_stub.py를 auth_jwt.py로 교체
2. dependencies.py의 import를 변경: from ..utils.auth_jwt import verify_jwt_token
3. get_current_user 함수의 Depends를 verify_jwt_token으로 변경
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Dict
from ..core.config import settings
from ..core.exceptions import UnauthorizedException

# OAuth2 스키마 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_jwt_token(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    JWT 토큰 검증 함수
    
    Args:
        token: OAuth2PasswordBearer에서 자동으로 추출한 토큰
    
    Returns:
        dict: 사용자 정보 {"user_id": int, "username": str}
    
    Raises:
        UnauthorizedException: 토큰이 유효하지 않은 경우
    """
    if not settings.SECRET_KEY:
        raise UnauthorizedException(
            message="JWT 설정이 올바르지 않습니다.",
            detail={"error": "SECRET_KEY not configured"}
        )
    
    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # 토큰에서 사용자 정보 추출
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if not user_id:
            raise UnauthorizedException(
                message="토큰에 사용자 정보가 없습니다.",
                detail={"payload": payload}
            )
        
        return {
            "user_id": int(user_id),
            "username": username or f"user_{user_id}"
        }
        
    except JWTError as e:
        raise UnauthorizedException(
            message="유효하지 않은 인증 토큰입니다.",
            detail={"error": str(e)}
        )
    except (ValueError, TypeError) as e:
        raise UnauthorizedException(
            message="토큰 형식이 올바르지 않습니다.",
            detail={"error": str(e)}
        )

