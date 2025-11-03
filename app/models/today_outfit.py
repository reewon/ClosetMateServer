from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class TodayOutfit(Base):
    __tablename__ = "today_outfit"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    상의_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    하의_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    신발_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    아우터_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 정의
    user = relationship("User", back_populates="today_outfit")
    
    # 각 카테고리별 아이템 관계 (optional)
    상의 = relationship("ClosetItem", foreign_keys=[상의_id], post_update=True)
    하의 = relationship("ClosetItem", foreign_keys=[하의_id], post_update=True)
    신발 = relationship("ClosetItem", foreign_keys=[신발_id], post_update=True)
    아우터 = relationship("ClosetItem", foreign_keys=[아우터_id], post_update=True)

