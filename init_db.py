"""
데이터베이스 초기화 스크립트
테스트용 초기 데이터를 생성합니다.

사용법:
    python init_db.py          # 테스트 데이터 삭제 후 재생성
    python init_db.py --reset  # 동일 (옵션은 호환성을 위해 유지)
"""

import sys
from app.core.database import SessionLocal
from app.core.init_db import init_test_data


def main():
    """메인 함수"""
    db = SessionLocal()
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--reset":
            print("Resetting test data...")
        else:
            print("Initializing test data...")
        init_test_data(db)
        
        print("\n[OK] Database initialization completed!")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

