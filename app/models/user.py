from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Firebase 인증 관련 필드
    firebase_uid = Column(String, unique=True, index=True, nullable=False)  # Firebase UID (고유 식별자)
    email = Column(String, unique=True, index=True, nullable=False)  # 이메일 (로그인 ID 역할)
    
    # 사용자 정보
    username = Column(String, nullable=False)  # 사용자 닉네임 (사용자 입력, unique 아님)
    gender = Column(String, nullable=False, default="남성")  # 성별 (남성, 여성) - 회원가입 시 사용자로부터 받음
    
    # password 필드는 Firebase에서 관리
    
    # 관계 정의
    closet_items = relationship("ClosetItem", back_populates="user", cascade="all, delete-orphan")
    today_outfit = relationship("TodayOutfit", back_populates="user", uselist=False, cascade="all, delete-orphan")
    favorite_outfits = relationship("FavoriteOutfit", back_populates="user", cascade="all, delete-orphan")