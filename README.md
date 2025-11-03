# ClosetMate Server

CLI 기반 클라이언트와 통신하는 Python FastAPI 서버입니다.

## 📁 프로젝트 구조

```
closet_app/
├── app/
│   ├── main.py                        # FastAPI 엔트리포인트
│   │
│   ├── core/                          # 핵심 설정 (DB, 환경, 예외)
│   │   ├── config.py                  # 환경 변수 관리 (후에 JWT key 추가)
│   │   ├── database.py                # SQLAlchemy 세션 관리
│   │   └── exceptions.py              # 공통 예외 처리 핸들러
│   │
│   ├── models/                        # ORM 모델 정의
│   │   ├── user.py                    # (선택) User 모델
│   │   ├── closet_item.py             # 옷장 아이템
│   │   ├── today_outfit.py            # 오늘의 코디
│   │   └── favorite_outfit.py         # 즐겨찾는 코디
│   │
│   ├── schemas/                       # Pydantic 스키마 정의 (요청/응답)
│   │   ├── user_schema.py
│   │   ├── closet_schema.py
│   │   ├── outfit_schema.py
│   │   └── favorite_schema.py
│   │
│   ├── routers/                       # 라우터 (API 엔드포인트)
│   │   ├── auth_router.py             # (추후 JWT 확장용, 현재는 생략 가능)
│   │   ├── closet_router.py           # 내 옷장 CRUD
│   │   ├── outfit_router.py           # 오늘의 코디 (AI 추천 포함)
│   │   └── favorite_router.py         # 즐겨찾는 코디 CRUD
│   │
│   ├── services/                      # 비즈니스 로직
│   │   ├── ai_service.py              # AI 추천 (Word2Vec / Gemini API 연결)
│   │   ├── outfit_service.py          # 코디 업데이트, 초기화 등
│   │   └── favorite_service.py        # 즐겨찾기 로직
│   │
│   ├── utils/                         # 유틸 함수 / 인증 / 공통 의존성
│   │   ├── auth_stub.py               # 테스트용 "Authorization: test-token" 인증
│   │   ├── dependencies.py            # get_db, get_current_user 등 공통 Depends
│   │   └── logger.py                  # 로그 유틸리티
│   │
│   └── __init__.py
│
├── closet.db                          # SQLite 데이터베이스 (자동 생성)
│
├── requirements.txt                   # 의존성 목록
│
├── .env                               # 환경 변수 파일 (JWT secret, DB URL 등)
│
├── alembic/                           # DB 마이그레이션 관리
│   ├── versions/
│   └── env.py
│
└── README.md                          # 협업용 프로젝트 개요 및 API 문서
```

## 🔐 인증 정책

- 모든 API는 `Authorization: test-token` 헤더가 필요합니다.
- 본 토큰은 테스트용 고정 계정(`user_id=1`, `username="test_user"`)으로 인증됩니다.
- JWT 로그인 기능은 추후 추가될 예정입니다.

## ❌ 에러 응답 포맷

모든 API는 실패 시 아래와 같은 일관된 JSON 구조로 에러를 반환합니다.
이를 통해 클라이언트는 상태 코드별로 예외를 구분하여 처리할 수 있습니다.

```json
{
  "status": "error",
  "code": 404,
  "error": "Not Found",
  "message": "요청하신 리소스를 찾을 수 없습니다.",
  "detail": {
    "resource": "closet_item",
    "id": 123
  }
}
```

### 📋 주요 에러 코드 정의

| 상태 코드   | error                     | message 예시                 | 설명                          |
|--------|---------------------------|------------------------------|-------------------------------|
| **400** | `"Bad Request"`           | `"잘못된 요청입니다. 입력값을 확인하세요."` | 요청 파라미터가 잘못됨                |
| **401** | `"Unauthorized"`          | `"유효하지 않은 인증 토큰입니다."`      | `Authorization` 헤더 누락 또는 오류 |
| **404** | `"Not Found"`             | `"요청하신 리소스를 찾을 수 없습니다."`   | 잘못된 ID 또는 존재하지 않는 데이터       |
| **409** | `"Conflict"`              | `"이미 존재하는 리소스입니다."`        | 중복된 등록 요청 등                 |
| **500** | `"Internal Server Error"` | `"서버 내부 오류가 발생했습니다."`      | 예기치 않은 서버 오류                |

## 🗄️ 데이터베이스 모델 구조

### 1. User

```python
from sqlalchemy import Column, Integer, String
from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # 지금은 단순 문자열 (test_user만 존재)
```

### 2. ClosetItem

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from ..core.database import Base

class ClosetItem(Base):
    __tablename__ = "closet_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String)   # 상의, 하의, 신발, 아우터
    name = Column(String)
    image_url = Column(String, nullable=True)
```

### 3. TodayOutfit

```python
from sqlalchemy import Column, Integer, ForeignKey, DateTime
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
```

### 4. FavoriteOutfit

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from ..core.database import Base

class FavoriteOutfit(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    상의_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    하의_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    신발_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    아우터_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 테이블 관계

- `users` → `closet_items`: 1:N (한 사용자가 여러 옷장 아이템 소유)
- `closet_items` → `today_outfit`: 1:1 (각 아이템은 오늘의 코디에 포함될 수 있음)
- `today_outfit` → `favorites`: 1:N (오늘의 코디를 여러 즐겨찾기로 저장 가능)

## 📡 API 명세서

### 1. Auth (테스트용 인증)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/auth/test-login` | 테스트 토큰 발급 | — | `{ "token": "test-token" }` |

### 2. Closet (내 옷장)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/closet/{category}` | 카테고리별 옷 조회 | — | `[{"id":1,"name":"화이트 티셔츠"}]` |
| `POST` | `/closet/{category}` | 옷 추가 | `{ "name": "그레이 슬랙스" }` | `{ "message": "추가 완료" }` |
| `DELETE` | `/closet/{item_id}` | 옷 삭제 | — | `{ "message": "삭제 완료" }` |

### 3. Today Outfit (오늘의 코디)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/outfit/today` | 오늘의 코디 보기 | — | `{ "상의": {"id": 1, "name": "화이트 티셔츠"}, "하의": {"id": 2, "name": "베이지 팬츠"}, ... }` |
| `PUT` | `/outfit/today` | 코디 아이템 선택/변경 | `{ "category": "상의", "item_id": 3 }` | `{ "message": "상의가 변경되었습니다." }` |
| `PUT` | `/outfit/clear` | 특정 카테고리 비우기 | `{ "category": "상의" }` | `{ "message": "상의가 비워졌습니다." }` |
| `POST` | `/outfit/recommend` | AI 추천 실행 | — | `{ "상의": {"id": ..., "name": "..."}, "하의": {"id": ..., "name": "..."}, ... }` |

### 4. Favorites (즐겨찾는 코디)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/favorites` | 즐겨찾는 코디 목록 | — | `[{"id":1,"name":"주말 데일리룩"}]` |
| `GET` | `/favorites/{id}` | 특정 코디 보기 | — | `{ "name": "주말 데일리룩", "상의": {"id": ..., "name": "..."}, ...}` |
| `POST` | `/favorites` | 오늘의 코디 즐겨찾기 저장 | `{ "name": "주말 데일리룩" }` | `{ "message": "저장 완료" }` |
| `PUT` | `/favorites/{id}` | 코디 이름 변경 | `{ "new_name": "주말 카페룩" }` | `{ "message": "이름이 변경되었습니다." }` |
| `DELETE` | `/favorites/{id}` | 코디 삭제 | — | `{ "message": "삭제 완료" }` |

