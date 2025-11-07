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


def init_test_data(db: Session) -> None:
    """
    테스트용 초기 데이터 생성
    conftest.py의 fixture 데이터와 동일한 구조로 생성
    
    Args:
        db: DB 세션
    """
    # 1. Test User 생성 (이미 존재하면 스킵)
    user = db.query(User).filter(User.id == TEST_USER_ID).first()
    if not user:
        user = User(
            id=TEST_USER_ID,
            username=TEST_USERNAME,
            password="test_password"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        pass
    
    # 2. Closet Items 생성 (이미 존재하면 스킵)
    existing_items_count = db.query(ClosetItem).filter(ClosetItem.user_id == user.id).count()
    if existing_items_count == 0:
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
    else:
        pass
    
    # 3. Today Outfit은 초기화하지 않음 (사용자가 직접 설정)
    # TodayOutfit 레코드는 사용자가 코디를 설정할 때 자동으로 생성됨
    
    # 4. Favorite Outfit 생성 (이미 존재하면 스킵)
    existing_favorites_count = db.query(FavoriteOutfit).filter(
        FavoriteOutfit.user_id == user.id,
        FavoriteOutfit.name == "weekend daily look"
    ).count()
    
    if existing_favorites_count == 0:
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
    else:
        pass


def reset_test_data(db: Session) -> None:
    """
    테스트 데이터를 초기화하고 다시 생성
    기존 데이터를 삭제한 후 새로 생성합니다.
    
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
    
    # 새로 생성
    init_test_data(db)

