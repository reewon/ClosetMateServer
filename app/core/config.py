from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./closet.db"
    
    # JWT 설정 (추후 사용)
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Gemini API 설정
    GEMINI_API_KEY: Optional[str] = None
    
    # 파일 저장 설정
    UPLOAD_DIR: str = "uploads"  # 옷 아이템 이미지 업로드 디렉토리
    
    # 프로젝트 설정
    PROJECT_NAME: str = "ClosetMate API"
    API_V1_PREFIX: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

