from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Dict
from ..core.database import get_db
from ..utils.auth_firebase import verify_firebase_auth
from ..models.user import User
from ..core.exceptions import NotFoundException
from ..utils.logger import logger


def get_db_session() -> Session:
    """
    DB 세션 의존성 함수
    
    Returns:
        Session: SQLAlchemy 세션
    """
    return Depends(get_db)


def get_current_user(
    # Firebase Auth 사용
    user_info: Dict[str, str] = Depends(verify_firebase_auth),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 사용자 정보를 가져오는 의존성 함수
    
    Firebase UID로 사용자를 조회하고, 없으면 자동 생성합니다.
    
    Args:
        user_info: verify_firebase_auth에서 반환한 사용자 정보
            - "firebase_uid": Firebase 사용자 UID
            - "email": 사용자 이메일
        db: DB 세션
    
    Returns:
        User: 현재 사용자 객체
    
    Raises:
        NotFoundException: 사용자를 찾을 수 없고 생성도 실패한 경우
    """
    firebase_uid = user_info.get("firebase_uid")
    email = user_info.get("email", "")
    
    if not firebase_uid:
        raise NotFoundException(
            message="Firebase UID를 찾을 수 없습니다.",
            detail={"user_info": user_info}
        )
    
    # Firebase UID로 사용자 조회
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if not user:
        # 사용자가 없으면 자동 생성
        # email은 Firebase 토큰에서 가져옴
        # username과 gender는 기본값 사용 (나중에 /auth/sync로 사용자가 입력한 값으로 업데이트)
        try:
            # username은 사용자가 입력하는 닉네임이므로 기본값 사용
            # 나중에 /auth/sync 엔드포인트로 사용자가 입력한 username과 gender로 업데이트
            username = f"user_{firebase_uid[:8]}"  # 기본값: "user_" + Firebase UID 앞 8자
            
            user = User(
                firebase_uid=firebase_uid,
                email=email,
                username=username,
                gender="남성"  # 기본값, 나중에 /auth/sync로 업데이트
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"새 사용자 자동 생성: firebase_uid={firebase_uid}, email={email}")
        except Exception as e:
            db.rollback()
            logger.error(f"사용자 자동 생성 실패: {e}")
            raise NotFoundException(
                message="사용자를 생성하는 중 오류가 발생했습니다.",
                detail={"firebase_uid": firebase_uid, "error": str(e)}
            )
    
    return user
