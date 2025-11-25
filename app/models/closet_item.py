from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class ClosetItem(Base):
    __tablename__ = "closet_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String)  # top, bottom, shoes, outer
    feature = Column(String, nullable=False)  # Gemini API로 추출한 피쳐 정보 (예: '하의_gray_cotton_숏 팬츠_남성_여름_casual')
    image_url = Column(String, nullable=True)
    
    # 관계 정의
    user = relationship("User", back_populates="closet_items")