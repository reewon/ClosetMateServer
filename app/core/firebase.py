"""
Firebase Admin SDK 초기화 및 토큰 검증 모듈
"""

import os
from typing import Dict, Optional
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError
from ..core.config import settings
from ..utils.logger import logger
from ..core.exceptions import UnauthorizedException


# Firebase Admin SDK 초기화 여부 추적
_firebase_initialized = False


def initialize_firebase() -> None:
    """
    Firebase Admin SDK 초기화
    
    FIREBASE_CREDENTIALS_PATH 환경 변수로 서비스 계정 키 파일 경로를 지정해야 합니다.(.env 파일에 설정)
    
    Raises:
        Exception: Firebase 초기화 실패 시
    """
    global _firebase_initialized
    
    if _firebase_initialized:
        logger.info("Firebase Admin SDK가 이미 초기화되어 있습니다.")
        return
    
    try:
        # 이미 초기화된 앱이 있는지 확인
        if len(firebase_admin._apps) > 0:
            logger.info("Firebase Admin SDK가 이미 초기화되어 있습니다.")
            _firebase_initialized = True
            return
        
        # 서비스 계정 키 파일 경로 사용
        if not settings.FIREBASE_CREDENTIALS_PATH:
            raise ValueError(
                "Firebase Admin SDK 초기화 실패: "
                ".env 파일에 FIREBASE_CREDENTIALS_PATH를 설정해주세요."
            )
        
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if not os.path.exists(cred_path):
            raise FileNotFoundError(
                f"Firebase 서비스 계정 키 파일을 찾을 수 없습니다: {cred_path}\n"
                f"파일 경로를 확인하거나 .env 파일의 FIREBASE_CREDENTIALS_PATH를 확인해주세요."
            )
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logger.info(f"Firebase Admin SDK 초기화 완료 (파일: {cred_path})")
        _firebase_initialized = True
        
    except FirebaseError as e:
        logger.error(f"Firebase 초기화 중 오류 발생: {e}")
        raise
    except Exception as e:
        logger.error(f"Firebase 초기화 중 예상치 못한 오류 발생: {e}")
        raise


def verify_firebase_token(id_token: str) -> Dict[str, str]:
    """
    Firebase ID 토큰 검증
    
    Args:
        id_token: 클라이언트에서 받은 Firebase ID 토큰
    
    Returns:
        dict: 검증된 토큰 정보
            - "firebase_uid": Firebase 사용자 UID
            - "email": 사용자 이메일
    
    Raises:
        UnauthorizedException: 토큰이 유효하지 않은 경우
    """
    # Firebase가 초기화되지 않았으면 초기화 시도
    if not _firebase_initialized:
        try:
            initialize_firebase()
        except Exception as e:
            logger.error(f"Firebase 초기화 실패: {e}")
            raise UnauthorizedException(
                message="Firebase 인증 서비스를 사용할 수 없습니다.",
                detail={"error": str(e)}
            )
    
    if not id_token:
        raise UnauthorizedException(
            message="인증 토큰이 제공되지 않았습니다.",
            detail={"error": "Missing token"}
        )
    
    try:
        # Firebase ID 토큰 검증
        decoded_token = auth.verify_id_token(id_token)
        
        # 토큰에서 필요한 정보 추출
        firebase_uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        
        if not firebase_uid:
            logger.warning("Firebase 토큰에 UID가 없습니다.")
            raise UnauthorizedException(
                message="토큰에 사용자 정보가 없습니다.",
                detail={"error": "Missing UID in token"}
            )
        
        logger.debug(f"Firebase 토큰 검증 성공: UID={firebase_uid}, Email={email}")
        
        return {
            "firebase_uid": firebase_uid,
            "email": email or ""  # email이 없을 수도 있음
        }
        
    except auth.InvalidIdTokenError as e:
        logger.warning(f"유효하지 않은 Firebase 토큰: {e}")
        raise UnauthorizedException(
            message="유효하지 않은 인증 토큰입니다.",
            detail={"error": "Invalid token", "detail": str(e)}
        )
    except auth.ExpiredIdTokenError as e:
        logger.warning(f"만료된 Firebase 토큰: {e}")
        raise UnauthorizedException(
            message="만료된 인증 토큰입니다. 다시 로그인해주세요.",
            detail={"error": "Expired token", "detail": str(e)}
        )
    except auth.RevokedIdTokenError as e:
        logger.warning(f"취소된 Firebase 토큰: {e}")
        raise UnauthorizedException(
            message="취소된 인증 토큰입니다. 다시 로그인해주세요.",
            detail={"error": "Revoked token", "detail": str(e)}
        )
    except FirebaseError as e:
        logger.error(f"Firebase 토큰 검증 중 오류 발생: {e}")
        raise UnauthorizedException(
            message="토큰 검증 중 오류가 발생했습니다.",
            detail={"error": "Firebase error", "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"토큰 검증 중 예상치 못한 오류 발생: {e}")
        raise UnauthorizedException(
            message="토큰 검증 중 오류가 발생했습니다.",
            detail={"error": "Unexpected error", "detail": str(e)}
        )

