from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class FavoriteOutfit(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    top_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    bottom_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    shoes_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    outer_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 정의
    user = relationship("User", back_populates="favorite_outfits")
    
    # 각 카테고리별 아이템 관계 (optional)
    # 'favorite_outfit.top'로 접근하면 top_id에 해당하는 ClosetItem 객체를 가져올 수 있음
    top = relationship("ClosetItem", foreign_keys=[top_id], post_update=True)
    bottom = relationship("ClosetItem", foreign_keys=[bottom_id], post_update=True)
    shoes = relationship("ClosetItem", foreign_keys=[shoes_id], post_update=True)
    outer = relationship("ClosetItem", foreign_keys=[outer_id], post_update=True)

