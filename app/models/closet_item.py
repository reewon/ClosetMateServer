from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class ClosetItem(Base):
    __tablename__ = "closet_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String)  # 상의, 하의, 신발, 아우터
    name = Column(String)
    image_url = Column(String, nullable=True)
    
    # 관계 정의
    user = relationship("User", back_populates="closet_items")

