from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 데이터베이스 엔진 생성
# PostgreSQL 또는 SQLite 모두 지원
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite 전용 옵션
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL (또는 다른 데이터베이스)
    engine = create_engine(settings.DATABASE_URL)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (모든 모델이 상속받을 클래스)
Base = declarative_base()


# 의존성 주입용 DB 세션 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

