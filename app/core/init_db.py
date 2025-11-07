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
    conftest.py의 fixture 데이터와 동일한 구조로 생성
    
    Args:
        db: DB 세션
    """
    # 1. Test User 생성
    user = User(
        id=TEST_USER_ID,
        username=TEST_USERNAME,
        password="test_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 2. Closet Items 생성
    items = [
        ClosetItem(user_id=user.id, category="top", name="white t-shirt"),
        ClosetItem(user_id=user.id, category="top", name="black hoodie"),
        ClosetItem(user_id=user.id, category="bottom", name="beige pants"),
        ClosetItem(user_id=user.id, category="bottom", name="black slacks"),
        ClosetItem(user_id=user.id, category="shoes", name="white sneakers"),
        ClosetItem(user_id=user.id, category="shoes", name="converse"),
        ClosetItem(user_id=user.id, category="outer", name="blue denim jacket"),
        ClosetItem(user_id=user.id, category="outer", name="black puffer"),
    ]
    
    for item in items:
        db.add(item)
    
    db.commit()
    
    for item in items:
        db.refresh(item)
    
    # 3. Today Outfit은 초기화하지 않음 (사용자가 직접 설정)
    # TodayOutfit 레코드는 사용자가 코디를 설정할 때 자동으로 생성됨
    
    # 4. Favorite Outfit 생성
    # Closet Items 조회 (인덱스 순서대로)
    closet_items = db.query(ClosetItem).filter(
        ClosetItem.user_id == user.id
    ).order_by(ClosetItem.id).all()
    
    if len(closet_items) >= 7:
        favorite = FavoriteOutfit(
            user_id=user.id,
            name="weekend daily look",
            top_id=closet_items[0].id,  # white t-shirt
            bottom_id=closet_items[2].id,  # beige pants
            shoes_id=closet_items[4].id,  # white sneakers
            outer_id=closet_items[6].id,  # blue denim jacket
        )
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
    else:
        print("[WARN] Not enough closet items to create favorite outfit")


def init_test_data(db: Session) -> None:
    """
    테스트용 초기 데이터 생성
    서버 재시작 시마다 테스트 유저 데이터를 삭제 후 재생성합니다.
    conftest.py의 fixture 데이터와 동일한 구조로 생성
    
    Args:
        db: DB 세션
    """
    _delete_test_data(db)
    _create_test_data(db)



