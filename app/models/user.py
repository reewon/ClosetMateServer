from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # 지금은 단순 문자열 (test_user만 존재)
    
    # 관계 정의
    closet_items = relationship("ClosetItem", back_populates="user", cascade="all, delete-orphan")
    today_outfit = relationship("TodayOutfit", back_populates="user", uselist=False, cascade="all, delete-orphan")
    favorite_outfits = relationship("FavoriteOutfit", back_populates="user", cascade="all, delete-orphan")

