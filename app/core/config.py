from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./closet.db"
    
    # Firebase 설정
    # 서비스 계정 키 JSON 파일 경로 지정 (.env 파일에 설정)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # Gemini API 설정
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"  # gemini-2.5-flash 또는 gemini-2.5-flash-lite
    
    # 파일 저장 설정
    UPLOAD_DIR: str = "uploads"  # 옷 아이템 이미지 업로드 디렉토리
    
    # 프로젝트 설정
    PROJECT_NAME: str = "ClosetMate API"
    API_V1_PREFIX: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

