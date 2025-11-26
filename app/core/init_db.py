"""
데이터베이스 초기화 모듈
테스트용 초기 데이터를 생성합니다.
"""

from sqlalchemy.orm import Session
from ..models.user import User
from ..models.closet_item import ClosetItem
from ..models.today_outfit import TodayOutfit
from ..models.favorite_outfit import FavoriteOutfit
from ..utils.auth_stub import TEST_USER_ID, TEST_USERNAME


def _delete_test_data(db: Session) -> None:
    """
    테스트 유저 데이터 삭제
    
    Args:
        db: DB 세션
    """
    user = db.query(User).filter(User.id == TEST_USER_ID).first()
    if user:
        # 관련 데이터 삭제 (cascade로 자동 삭제되지만 명시적으로)
        db.query(FavoriteOutfit).filter(FavoriteOutfit.user_id == user.id).delete()
        db.query(TodayOutfit).filter(TodayOutfit.user_id == user.id).delete()
        db.query(ClosetItem).filter(ClosetItem.user_id == user.id).delete()
        db.query(User).filter(User.id == TEST_USER_ID).delete()
        db.commit()


def _create_test_data(db: Session) -> None:
    """
    테스트용 초기 데이터 생성
    
    Args:
        db: DB 세션
    """
    # Test User 생성
    user = User(
        id=TEST_USER_ID,
        firebase_uid="test_firebase_uid",  # 테스트용 Firebase UID
        email="test@example.com",  # 테스트용 이메일
        username=TEST_USERNAME,
        gender="남성"  # 기본값
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Closet Items, Today Outfit, Favorite Outfit은 생성하지 않음
    # 사용자가 직접 옷을 업로드하고 코디를 설정할 수 있습니다.


def init_test_data(db: Session) -> None:
    """
    테스트용 초기 데이터 생성
    테스트 유저가 없을 때만 생성합니다.
    (기존 데이터는 유지하여 사용자가 추가한 데이터가 삭제되지 않도록 함)
    
    **주의**: Firebase Auth를 사용하는 경우 테스트 사용자 생성을 비활성화합니다.
    Firebase 사용자는 로그인 시 자동으로 생성됩니다.
    
    Args:
        db: DB 세션
    """
    from ..utils.auth_stub import TEST_USER_ID
    
    # Firebase Auth를 사용하므로 테스트 사용자 생성을 비활성화
    # Firebase 사용자는 로그인 시 get_current_user에서 자동 생성됨
    return
    


