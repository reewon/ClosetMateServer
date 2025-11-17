"""
ClosetMate API 메인 진입점
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.database import engine, Base, SessionLocal
from .core.init_db import init_test_data
from .routers import (
    auth_router,
    closet_router,
    outfit_router,
    favorite_router
)
from .models import User, ClosetItem, TodayOutfit, FavoriteOutfit  # 테이블 생성용 import

# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="ClosetMate API - 옷장 관리 및 코디 추천 서비스"
)

# CORS 설정 (필요한 경우)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 origin만 허용하도록 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 테이블 생성 및 초기 데이터 생성
@app.on_event("startup")
def on_startup():
    """
    앱 시작 시 데이터베이스 테이블 생성 및 테스트용 초기 데이터 생성
    """
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 테스트용 초기 데이터 생성 (이미 존재하면 스킵)
    db = SessionLocal()
    try:
        init_test_data(db)
    finally:
        db.close()


# 정적 파일 서빙 (이미지 파일 제공)
# uploads 폴더를 /uploads 경로로 제공
import os
uploads_dir = settings.UPLOAD_DIR
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 라우터 등록
app.include_router(auth_router, prefix="/api/v1")
app.include_router(closet_router, prefix="/api/v1")
app.include_router(outfit_router, prefix="/api/v1")
app.include_router(favorite_router, prefix="/api/v1")


@app.get("/")
def root():
    """
    루트 엔드포인트
    """
    return {
        "message": "ClosetMate API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {"status": "healthy"}

