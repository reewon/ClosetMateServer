from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class FavoriteOutfit(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    상의_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    하의_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    신발_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    아우터_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 정의
    user = relationship("User", back_populates="favorite_outfits")
    
    # 각 카테고리별 아이템 관계 (optional)
    # 'favorite_outfit.상의'로 접근하면 상의_id에 해당하는 ClosetItem 객체를 가져올 수 있음
    상의 = relationship("ClosetItem", foreign_keys=[상의_id], post_update=True)
    하의 = relationship("ClosetItem", foreign_keys=[하의_id], post_update=True)
    신발 = relationship("ClosetItem", foreign_keys=[신발_id], post_update=True)
    아우터 = relationship("ClosetItem", foreign_keys=[아우터_id], post_update=True)

