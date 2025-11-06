"""
pytest fixtures 설정 파일
테스트용 데이터베이스, 클라이언트, 공통 데이터 등을 제공
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.closet_item import ClosetItem
from app.models.today_outfit import TodayOutfit
from app.models.favorite_outfit import FavoriteOutfit


# 테스트용 데이터베이스 URL (메모리 DB 사용)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    각 테스트마다 새로운 인메모리 데이터베이스를 생성하는 fixture
    테스트가 끝나면 자동으로 정리됨
    
    Yields:
        Session: 테스트용 DB 세션
    """
    # 테스트용 엔진 생성
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # 테스트용 세션 팩토리 생성
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 세션 생성
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # 테이블 삭제 (다음 테스트를 위해 깨끗한 상태로)
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    FastAPI TestClient fixture
    test_db를 의존성으로 주입
    
    Args:
        test_db: 테스트용 DB 세션
    
    Yields:
        TestClient: FastAPI 테스트 클라이언트
    """
    # test_db와 같은 엔진에서 생성된 connection 사용
    connection = test_db.get_bind().connect()
    transaction = connection.begin()
    
    # 트랜잭션 기반 세션 생성
    test_session = Session(bind=connection)
    
    def override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    # 의존성 오버라이드
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # 정리
    test_session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers() -> dict:
    """
    테스트용 인증 헤더 fixture
    
    Returns:
        dict: Authorization 헤더
    """
    return {"Authorization": "test-token"}


@pytest.fixture(scope="function")
def test_user(test_db: Session) -> User:
    """
    테스트용 사용자 생성 fixture
    
    Args:
        test_db: 테스트용 DB 세션
    
    Returns:
        User: 테스트용 사용자 객체
    """
    user = User(
        id=1,
        username="test_user",
        password="test_password"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_closet_items(test_db: Session, test_user: User) -> list[ClosetItem]:
    """
    테스트용 옷장 아이템들을 생성하는 fixture
    각 카테고리별로 2개씩 생성
    
    Args:
        test_db: 테스트용 DB 세션
        test_user: 테스트용 사용자
    
    Returns:
        list[ClosetItem]: 생성된 옷장 아이템 리스트
    """
    items = [
        ClosetItem(user_id=test_user.id, category="top", name="화이트 티셔츠"),
        ClosetItem(user_id=test_user.id, category="top", name="블랙 후드티"),
        ClosetItem(user_id=test_user.id, category="bottom", name="베이지 팬츠"),
        ClosetItem(user_id=test_user.id, category="bottom", name="블랙 슬랙스"),
        ClosetItem(user_id=test_user.id, category="shoes", name="화이트 운동화"),
        ClosetItem(user_id=test_user.id, category="shoes", name="컨버스"),
        ClosetItem(user_id=test_user.id, category="outer", name="블루 데님 재킷"),
        ClosetItem(user_id=test_user.id, category="outer", name="블랙 패딩"),
    ]
    
    for item in items:
        test_db.add(item)
    
    test_db.commit()
    
    for item in items:
        test_db.refresh(item)
    
    return items


@pytest.fixture(scope="function")
def test_today_outfit(test_db: Session, test_user: User, test_closet_items: list[ClosetItem]) -> TodayOutfit:
    """
    테스트용 오늘의 코디를 생성하는 fixture
    
    Args:
        test_db: 테스트용 DB 세션
        test_user: 테스트용 사용자
        test_closet_items: 테스트용 옷장 아이템들
    
    Returns:
        TodayOutfit: 생성된 오늘의 코디 객체
    """
    # 각 카테고리의 첫 번째 아이템 선택
    outfit = TodayOutfit(
        user_id=test_user.id,
        top_id=test_closet_items[0].id,  # 화이트 티셔츠
        bottom_id=test_closet_items[2].id,  # 베이지 팬츠
        shoes_id=test_closet_items[4].id,  # 화이트 운동화
        outer_id=test_closet_items[6].id,  # 블루 데님 재킷
    )
    
    test_db.add(outfit)
    test_db.commit()
    test_db.refresh(outfit)
    
    return outfit


@pytest.fixture(scope="function")
def test_favorite_outfit(test_db: Session, test_user: User, test_closet_items: list[ClosetItem]) -> FavoriteOutfit:
    """
    테스트용 즐겨찾는 코디를 생성하는 fixture
    
    Args:
        test_db: 테스트용 DB 세션
        test_user: 테스트용 사용자
        test_closet_items: 테스트용 옷장 아이템들
    
    Returns:
        FavoriteOutfit: 생성된 즐겨찾는 코디 객체
    """
    favorite = FavoriteOutfit(
        user_id=test_user.id,
        name="주말 데일리룩",
        top_id=test_closet_items[0].id,  # 화이트 티셔츠
        bottom_id=test_closet_items[2].id,  # 베이지 팬츠
        shoes_id=test_closet_items[4].id,  # 화이트 운동화
        outer_id=test_closet_items[6].id,  # 블루 데님 재킷
    )
    
    test_db.add(favorite)
    test_db.commit()
    test_db.refresh(favorite)
    
    return favorite


@pytest.fixture(scope="function")
def empty_today_outfit(test_db: Session, test_user: User) -> TodayOutfit:
    """
    빈 오늘의 코디를 생성하는 fixture (모든 아이템이 None)
    
    Args:
        test_db: 테스트용 DB 세션
        test_user: 테스트용 사용자
    
    Returns:
        TodayOutfit: 빈 오늘의 코디 객체
    """
    outfit = TodayOutfit(
        user_id=test_user.id,
        top_id=None,
        bottom_id=None,
        shoes_id=None,
        outer_id=None,
    )
    
    test_db.add(outfit)
    test_db.commit()
    test_db.refresh(outfit)
    
    return outfit

