from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class TodayOutfit(Base):
    __tablename__ = "today_outfit"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    top_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    bottom_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    shoes_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    outer_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 정의
    user = relationship("User", back_populates="today_outfit")
    
    # 각 카테고리별 아이템 관계 (optional)
    top = relationship("ClosetItem", foreign_keys=[top_id], post_update=True)
    bottom = relationship("ClosetItem", foreign_keys=[bottom_id], post_update=True)
    shoes = relationship("ClosetItem", foreign_keys=[shoes_id], post_update=True)
    outer = relationship("ClosetItem", foreign_keys=[outer_id], post_update=True)

