from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Dict
from ..core.database import get_db
from ..utils.auth_stub import verify_test_token, TEST_USER_ID
# JWT 전환 시: 아래 import로 변경
# from ..utils.auth_jwt import verify_jwt_token
from ..models.user import User
from ..core.exceptions import NotFoundException


def get_db_session() -> Session:
    """
    DB 세션 의존성 함수
    
    Returns:
        Session: SQLAlchemy 세션
    """
    return Depends(get_db)


def get_current_user(
    # 테스트용: verify_test_token 사용
    # JWT 전환 시: Depends(verify_test_token) → Depends(verify_jwt_token)로 변경
    user_info: Dict = Depends(verify_test_token),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 사용자 정보를 가져오는 의존성 함수
    
    JWT 전환 시:
    1. import를 verify_jwt_token으로 변경
    2. Depends(verify_test_token) → Depends(verify_jwt_token)로 변경
    3. 자동 생성 로직 제거 (아래 if문 전체 제거)
    
    Args:
        user_info: verify_test_token 또는 verify_jwt_token에서 반환한 사용자 정보
        db: DB 세션
    
    Returns:
        User: 현재 사용자 객체
    
    Raises:
        NotFoundException: 사용자를 찾을 수 없는 경우
    """
    user = db.query(User).filter(User.id == user_info["user_id"]).first()
    
    if not user:
        # 테스트용: 고정된 테스트 사용자만 자동 생성
        # JWT 전환 시 이 블록 전체를 제거하고 예외만 발생시켜야 함
        if user_info["user_id"] == TEST_USER_ID and user_info["username"] == "test_user":
            user = User(
                id=TEST_USER_ID,
                username=user_info["username"],
                password="test_password"  # 테스트용
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # 테스트용이 아닌 경우 예외 발생
            # JWT 전환 시에는 이 else 블록만 남김
            raise NotFoundException(
                message="사용자를 찾을 수 없습니다.",
                detail={"user_id": user_info["user_id"]}
            )
    
    return user

# JWT 전환 후에는 이 함수를 삭제하고 get_current_user만 사용


