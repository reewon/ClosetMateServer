"""
PostgreSQL 마이그레이션 스크립트
SQLAlchemy를 사용하여 PostgreSQL에 테이블 생성
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models import User, ClosetItem, TodayOutfit, FavoriteOutfit
from app.core.config import settings
from app.utils.logger import logger

def migrate_to_postgresql():
    """
    PostgreSQL에 테이블 생성
    """
    print("=" * 60)
    print("PostgreSQL 마이그레이션 스크립트")
    print("=" * 60)
    print()
    
    # DATABASE_URL 확인
    database_url = settings.DATABASE_URL
    print(f"데이터베이스 URL: {database_url[:50]}..." if len(database_url) > 50 else f"데이터베이스 URL: {database_url}")
    print()
    
    # PostgreSQL인지 확인
    if not database_url.startswith("postgresql"):
        print("⚠️  경고: DATABASE_URL이 PostgreSQL이 아닙니다.")
        print(f"   현재: {database_url}")
        print("   .env 파일에 DATABASE_URL을 PostgreSQL로 설정하세요.")
        print("   예: postgresql://postgres:password@localhost:5432/closetmate")
        response = input("\n계속하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("취소되었습니다.")
            return
    
    print("PostgreSQL에 테이블 생성 중...")
    print()
    
    try:
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        
        print("✅ 테이블 생성 완료!")
        print()
        print("생성된 테이블:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        print()
        print("=" * 60)
        print("마이그레이션 완료!")
        print("=" * 60)
        print()
        print("다음 단계:")
        print("  1. 서버를 시작하여 연결 테스트")
        print("  2. API를 통해 데이터 생성/조회 테스트")
        
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        print()
        print("확인 사항:")
        print("  1. PostgreSQL 서비스가 실행 중인지 확인")
        print("  2. .env 파일의 DATABASE_URL이 올바른지 확인")
        print("  3. 데이터베이스 'closetmate'가 생성되었는지 확인")
        print("  4. 사용자명과 비밀번호가 올바른지 확인")
        raise

if __name__ == "__main__":
    migrate_to_postgresql()

