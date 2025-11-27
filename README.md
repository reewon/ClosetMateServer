# ClosetMate Server

CLI 기반 클라이언트와 통신하는 Python FastAPI 서버입니다.

## 🛠️ 개발 환경

### 필수 요구사항

- **Python**: 3.8 이상
- **PostgreSQL**: 18.0 이상 (데이터베이스)
- **Firebase**: Firebase Authentication (인증 서비스)

### 주요 기술 스택

#### 백엔드 프레임워크
- **FastAPI**: 0.104.1 이상 - RESTful API 프레임워크
- **Uvicorn**: 0.24.0 이상 - ASGI 서버

#### 데이터베이스
- **PostgreSQL**: 18.0 - 프로덕션 데이터베이스
- **SQLAlchemy**: 2.0.23 이상 - ORM
- **psycopg2-binary**: 2.9.0 이상 - PostgreSQL 어댑터

#### 인증
- **Firebase Admin SDK**: 6.0.0 이상 - Firebase Authentication 서버 사이드 검증

#### AI/ML
- **Google Generative AI**: 0.8.0 이상 - Gemini API (이미지 분석, feature 추출)
- **Word2Vec**: AI 추천 모델 (ai_recommendation 모듈)

#### 기타
- **Pydantic Settings**: 2.0.0 이상 - 환경 변수 관리
- **Python Multipart**: 0.0.6 이상 - 파일 업로드 처리

### 개발 도구

- **테스트**: pytest 7.4.0 이상
- **코드 커버리지**: pytest-cov
- **HTTP 클라이언트**: httpx (테스트용)

## 📁 프로젝트 구조

```
ClosetmateServer/
├── app/                                # FastAPI 애플리케이션
│   ├── main.py                        # FastAPI 엔트리포인트
│   │
│   ├── core/                          # 핵심 설정 (DB, 환경, 예외)
│   │   ├── config.py                  # 환경 변수 관리 (Gemini API 키, DB URL 등)
│   │   ├── database.py                # SQLAlchemy 세션 관리
│   │   ├── exceptions.py              # 공통 예외 처리 핸들러
│   │   └── init_db.py                 # 데이터베이스 초기화 및 테스트 데이터 생성
│   │
│   ├── models/                        # ORM 모델 정의
│   │   ├── user.py                    # User 모델
│   │   ├── closet_item.py             # 옷장 아이템 (feature 필수)
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
│   │   ├── auth_router.py             # 인증 (테스트용 토큰 발급)
│   │   ├── closet_router.py           # 내 옷장 CRUD (이미지 업로드, Gemini API 연동)
│   │   ├── outfit_router.py           # 오늘의 코디 (AI 추천 포함)
│   │   └── favorite_router.py         # 즐겨찾는 코디 CRUD
│   │
│   ├── services/                      # 비즈니스 로직
│   │   ├── ai_service.py              # AI 추천 서비스 (ai_recommendation 모듈 연동)
│   │   ├── gemini_service.py          # Gemini API 연동 (이미지 분석, feature 추출)
│   │   ├── storage_service.py         # 이미지 파일 저장/삭제 서비스
│   │   ├── outfit_service.py          # 코디 업데이트, 초기화 등
│   │   └── favorite_service.py        # 즐겨찾기 로직
│   │
│   └── utils/                         # 유틸 함수 / 인증 / 공통 의존성
│       ├── auth_stub.py               # 테스트용 "Authorization: test-token" 인증
│       ├── dependencies.py            # get_db, get_current_user 등 공통 Depends
│       └── logger.py                  # 로그 유틸리티
│
├── ai_recommendation/                  # AI 추천 모델 모듈
│   ├── model_loader.py                # Word2Vec 모델 로더
│   ├── recommendation_engine.py      # 코디 추천 엔진 (Word2Vec, 색상/재질 임베딩)
│   ├── train_model.py                 # 모델 학습 스크립트
│   ├── models/                        # 학습된 모델 파일
│   │   ├── w2v_model.model            # Word2Vec 모델
│   │   ├── color_fabric_model.model  # 색상/재질 임베딩 모델
│   │   ├── merged_df.pkl              # 병합된 데이터프레임
│   │   ├── filtered_df.pkl            # 필터링된 데이터프레임
│   │   └── params.json                # 모델 파라미터
│   ├── data/                          # 학습 데이터
│   │   ├── sentence_comb_fin.csv
│   │   └── total_final_data.csv
│   ├── README.md                      # AI 추천 모듈 사용법
│   └── SERVER_INTEGRATION.md          # 서버 통합 가이드
│
├── tests/                              # 테스트 코드
│   ├── conftest.py                    # pytest fixtures (테스트 DB, 클라이언트 등)
│   ├── fixtures/                      # 테스트용 fixture 파일
│   │   └── images/                    # 테스트용 이미지 파일
│   │       ├── test_top.jpg
│   │       ├── test_bottom.jpg
│   │       ├── test_shoes.jpg
│   │       └── test_outer.jpg
│   ├── test_routers/                  # 라우터 테스트
│   │   ├── test_auth_router.py
│   │   ├── test_closet_router.py      # 옷장 CRUD 테스트 (Mock 및 실제 이미지 통합 테스트)
│   │   ├── test_outfit_router.py      # 코디 테스트
│   │   └── test_favorite_router.py    # 즐겨찾기 테스트
│   ├── test_services/                 # 서비스 테스트
│   │   └── test_ai_recommendation.py  # AI 추천 서비스 테스트
│   ├── test_models/                   # 모델 테스트
│   └── test_utils/                    # 유틸리티 테스트
│
├── uploads/                            # 사용자 업로드 이미지 저장 디렉터리
│   └── user_{user_id}/                # 사용자별 디렉터리
│
├── closet.db                           # SQLite 데이터베이스 (자동 생성)
│
├── requirements.txt                    # 의존성 목록
│
├── pytest.ini                          # pytest 설정 파일
│
├── .env                                # 환경 변수 파일 (GEMINI_API_KEY, DB URL 등)
│
├── init_db.py                          # 데이터베이스 초기화 스크립트
│
└── README.md                           # 프로젝트 개요 및 API 문서
```

## 🔐 인증 정책

- 모든 API는 `Authorization: Bearer <firebase_id_token>` 헤더가 필요합니다.
- Firebase Authentication을 사용하여 인증합니다.
- 클라이언트에서 Firebase 로그인 후 받은 ID 토큰을 `Authorization: Bearer <token>` 형식으로 전송해야 합니다.
- **테스트용**: `/api/v1/auth/test-login` 엔드포인트로 테스트 토큰을 발급받을 수 있습니다 (개발/테스트용).

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
from sqlalchemy.orm import relationship
from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Firebase 인증 관련 필드
    firebase_uid = Column(String, unique=True, index=True, nullable=False)  # Firebase UID (고유 식별자)
    email = Column(String, unique=True, index=True, nullable=False)  # 이메일 (로그인 ID 역할)
    
    # 사용자 정보
    username = Column(String, nullable=False)  # 사용자명 (email이 고유 식별자)
    gender = Column(String, nullable=False, default="남성")  # 성별 (남성, 여성) - Gemini API feature 추출 시 사용
    
    # password 필드는 Firebase에서 관리
    
    # 관계 정의
    closet_items = relationship("ClosetItem", back_populates="user", cascade="all, delete-orphan")
    today_outfit = relationship("TodayOutfit", back_populates="user", uselist=False, cascade="all, delete-orphan")
    favorite_outfits = relationship("FavoriteOutfit", back_populates="user", cascade="all, delete-orphan")
```

### 2. ClosetItem

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class ClosetItem(Base):
    __tablename__ = "closet_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String)  # top, bottom, shoes, outer
    feature = Column(String, nullable=False)  # Gemini API로 추출한 피쳐 정보 (필수)
    # 형식: '카테고리_색상_재질_상세정보_성별_계절_스타일'
    # 예: '하의_gray_cotton_숏 팬츠_남성_여름_casual'
    image_url = Column(String, nullable=True)  # 이미지 파일 경로 (예: "uploads/user_1/item_1_abc123.jpg")
    
    # 관계 정의
    user = relationship("User", back_populates="closet_items")
```

**주요 특징:**
- `feature` 필드는 **필수 필드** (`nullable=False`)
- Gemini API로 이미지에서 자동 추출됨
- AI 추천 엔진에서 사용하는 핵심 데이터

### 3. TodayOutfit

```python
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
    outer_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)  # 선택 사항
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 정의
    user = relationship("User", back_populates="today_outfit")
    top = relationship("ClosetItem", foreign_keys=[top_id], post_update=True)
    bottom = relationship("ClosetItem", foreign_keys=[bottom_id], post_update=True)
    shoes = relationship("ClosetItem", foreign_keys=[shoes_id], post_update=True)
    outer = relationship("ClosetItem", foreign_keys=[outer_id], post_update=True)
```

**주요 특징:**
- 사용자당 하나의 레코드만 존재 (user_id가 primary key)
- `outer`는 선택 사항 (nullable=True)
- 필수 카테고리: top, bottom, shoes

### 4. FavoriteOutfit

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class FavoriteOutfit(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)  # 즐겨찾기 이름 (예: "주말 데일리룩")
    top_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    bottom_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    shoes_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)
    outer_id = Column(Integer, ForeignKey("closet_items.id"), nullable=True)  # 선택 사항
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 정의
    user = relationship("User", back_populates="favorite_outfits")
    top = relationship("ClosetItem", foreign_keys=[top_id], post_update=True)
    bottom = relationship("ClosetItem", foreign_keys=[bottom_id], post_update=True)
    shoes = relationship("ClosetItem", foreign_keys=[shoes_id], post_update=True)
    outer = relationship("ClosetItem", foreign_keys=[outer_id], post_update=True)
```

**주요 특징:**
- `outer`는 선택 사항 (nullable=True)
- 저장 시 필수 카테고리: top, bottom, shoes (outer는 선택)
- 같은 이름의 즐겨찾기는 중복 불가

### 테이블 관계

- **`users` → `closet_items`**: 1:N
  - 한 사용자가 여러 옷장 아이템 소유
  - 사용자 삭제 시 관련 아이템도 함께 삭제 (cascade)
  
- **`users` → `today_outfit`**: 1:1
  - 사용자당 하나의 오늘의 코디만 존재
  - 사용자 삭제 시 함께 삭제 (cascade)
  
- **`users` → `favorite_outfits`**: 1:N
  - 한 사용자가 여러 즐겨찾기 코디 저장 가능
  - 사용자 삭제 시 관련 즐겨찾기도 함께 삭제 (cascade)
  
- **`closet_items` → `today_outfit`**: N:1
  - 각 아이템은 오늘의 코디의 특정 카테고리에 포함될 수 있음
  - top_id, bottom_id, shoes_id, outer_id로 참조
  
- **`closet_items` → `favorite_outfits`**: N:1
  - 각 아이템은 여러 즐겨찾기 코디에 포함될 수 있음
  - top_id, bottom_id, shoes_id, outer_id로 참조

## 📡 API 명세서

> **Base URL**: `/api/v1`  
> 모든 엔드포인트는 `/api/v1` prefix를 사용합니다. (향후 AI 모델 업그레이드 시 v2로 확장 가능)

### 1. Auth (인증)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/api/v1/auth/test-login` | 테스트 토큰 발급 (개발/테스트용) | — | `{ "token": "test-token" }` |
| `GET` | `/api/v1/auth/me` | 현재 사용자 정보 조회 | `Authorization: Bearer <token>` | `{ "id": 1, "firebase_uid": "...", "email": "...", "username": "...", "gender": "남성" }` |
| `POST` | `/api/v1/auth/sync` | 사용자 정보 동기화 (회원가입 후 username, gender 업데이트) | `{ "username": "...", "gender": "남성" }` | `{ "id": 1, "firebase_uid": "...", "email": "...", "username": "...", "gender": "남성" }` |

### 2. Closet (내 옷장)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/api/v1/closet/{category}` | 카테고리별 옷 조회 | — | `[{"id":1,"feature":"상의_white_cotton_반소매 티셔츠_남성_여름_casual","image_url":"uploads/user_1/item_1_abc123.jpg"}]` |
| `POST` | `/api/v1/closet/{category}` | 옷 추가 (이미지 업로드) | `multipart/form-data` (image 파일) | `{ "message": "추가 완료" }` |
| `DELETE` | `/api/v1/closet/{item_id}` | 옷 삭제 | — | `{ "message": "삭제 완료" }` |

### 3. Today Outfit (오늘의 코디)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/api/v1/outfit/today` | 오늘의 코디 보기 | — | `{ "top": {"id": 1, "image_url": "uploads/user_1/item_1_abc123.jpg"}, "bottom": {"id": 2, "image_url": "uploads/user_1/item_2_def456.jpg"}, ... }` |
| `PUT` | `/api/v1/outfit/today` | 코디 아이템 선택/변경 | `{ "category": "top", "item_id": 3 }` | `{ "message": "top 변경 완료" }` |
| `PUT` | `/api/v1/outfit/clear` | 특정 카테고리 비우기 | `{ "category": "top" }` | `{ "message": "top 비우기 완료" }` |
| `POST` | `/api/v1/outfit/recommend` | AI 추천 실행 (Word2Vec 기반) | — | `{ "top": {"id": ..., "image_url": "..."}, "bottom": {"id": ..., "image_url": "..."}, ... }` |

### 4. Favorites (즐겨찾는 코디)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/api/v1/favorites` | 즐겨찾는 코디 목록 | — | `[{"id":1,"name":"주말 데일리룩"}]` |
| `GET` | `/api/v1/favorites/{id}` | 특정 코디 보기 | — | `{ "name": "주말 데일리룩", "top": {"id": ..., "image_url": "..."}, ...}` |
| `POST` | `/api/v1/favorites` | 오늘의 코디 즐겨찾기 저장 | `{ "name": "주말 데일리룩" }` | `{ "message": "저장 완료" }` |
| `PUT` | `/api/v1/favorites/{id}` | 코디 이름 변경 | `{ "new_name": "주말 카페룩" }` | `{ "message": "이름이 변경되었습니다." }` |
| `DELETE` | `/api/v1/favorites/{id}` | 코디 삭제 | — | `{ "message": "삭제 완료" }` |

## 📋 상세 응답 구조

### 1. Auth API

#### `GET /api/v1/auth/test-login`

**설명**
- 개발/테스트용 테스트 토큰 발급 엔드포인트입니다.
- 프로덕션 환경에서는 사용하지 않는 것을 권장합니다.

**정상 응답 (200 OK)**
```json
{
  "token": "test-token"
}
```

---

#### `GET /api/v1/auth/me`

**설명**
- 현재 인증된 사용자의 정보를 조회합니다.
- Firebase ID 토큰이 필요합니다 (`Authorization: Bearer <firebase_id_token>`).

**정상 응답 (200 OK)**
```json
{
  "id": 1,
  "firebase_uid": "abc123def456",
  "email": "user@example.com",
  "username": "user_abc123",
  "gender": "남성"
}
```

**비정상 응답 (401 Unauthorized) - 토큰이 제공되지 않은 경우**
```json
{
  "status": "error",
  "code": 401,
  "error": "Unauthorized",
  "message": "인증 토큰이 제공되지 않았습니다.",
  "detail": {
    "header": "Authorization"
  }
}
```

**비정상 응답 (401 Unauthorized) - 유효하지 않은 토큰**
```json
{
  "status": "error",
  "code": 401,
  "error": "Unauthorized",
  "message": "유효하지 않은 인증 토큰입니다.",
  "detail": {}
}
```

---

#### `POST /api/v1/auth/sync`

**설명**
- 회원가입 후 사용자 정보(username, gender)를 동기화하는 엔드포인트입니다.
- Firebase 로그인 후 첫 API 호출 시 사용자가 자동 생성되지만, 기본값으로 설정됩니다.
- 이 엔드포인트를 통해 사용자가 직접 username과 gender를 설정할 수 있습니다.
- `gender`는 "남성" 또는 "여성"만 입력 가능합니다.

**요청 본문**
```json
{
  "username": "홍길동",
  "gender": "남성"
}
```

**정상 응답 (200 OK)**
```json
{
  "id": 1,
  "firebase_uid": "abc123def456",
  "email": "user@example.com",
  "username": "홍길동",
  "gender": "남성"
}
```

**비정상 응답 (400 Bad Request) - 잘못된 gender 값**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "성별은 '남성' 또는 '여성'만 입력 가능합니다.",
  "detail": {
    "gender": "기타"
  }
}
```

**비정상 응답 (400 Bad Request) - username이 공백인 경우**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "사용자명은 공백만으로 구성될 수 없습니다.",
  "detail": {
    "username": "   "
  }
}
```

**비정상 응답 (401 Unauthorized) - 인증 토큰이 없는 경우**
```json
{
  "status": "error",
  "code": 401,
  "error": "Unauthorized",
  "message": "인증 토큰이 제공되지 않았습니다.",
  "detail": {
    "header": "Authorization"
  }
}
```

---

### 2. Closet API

#### `GET /api/v1/closet/{category}`

**정상 응답 (200 OK)**
```json
[
  {
    "id": 1,
    "feature": "상의_white_cotton_반소매 티셔츠_남성_여름_casual",
    "image_url": "uploads/user_1/item_1_abc123.jpg"
  },
  {
    "id": 2,
    "feature": "상의_black_cotton_후드 티셔츠_남성_가을_street",
    "image_url": "uploads/user_1/item_2_def456.jpg"
  }
]
```

**빈 목록 응답 (200 OK)**
```json
[]
```

#### `POST /api/v1/closet/{category}`

**요청 형식**
- Content-Type: `multipart/form-data`
- 필드: `image` (이미지 파일)
- 지원 형식: jpg, jpeg, png, gif, webp

**정상 응답 (200 OK)**
```json
{
  "message": "추가 완료"
}
```

**비정상 응답 (400 Bad Request) - 잘못된 카테고리**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "잘못된 카테고리입니다. 가능한 값: top, bottom, shoes, outer",
  "detail": {
    "category": "잘못된카테고리"
  }
}
```

**비정상 응답 (400 Bad Request) - 이미지 파일이 아닌 경우**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "이미지 파일만 업로드 가능합니다.",
  "detail": {
    "content_type": "application/pdf"
  }
}
```

**비정상 응답 (400 Bad Request) - Gemini API 오류**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "이미지 분석 중 오류가 발생했습니다: ...",
  "detail": {
    "error": "..."
  }
}
```

#### `DELETE /api/v1/closet/{item_id}`

**정상 응답 (200 OK)**
```json
{
  "message": "삭제 완료"
}
```

**비정상 응답 (404 Not Found)**
```json
{
  "status": "error",
  "code": 404,
  "error": "Not Found",
  "message": "옷장 아이템을 찾을 수 없습니다.",
  "detail": {
    "resource": "closet_item",
    "id": 999
  }
}
```

---

### 3. Today Outfit API

#### `GET /api/v1/outfit/today`

**정상 응답 - 완전한 코디 (200 OK)**
```json
{
  "top": {
    "id": 1,
    "image_url": "uploads/user_1/item_1_abc123.jpg"
  },
  "bottom": {
    "id": 2,
    "image_url": "uploads/user_1/item_2_def456.jpg"
  },
  "shoes": {
    "id": 3,
    "image_url": "uploads/user_1/item_3_ghi789.jpg"
  },
  "outer": {
    "id": 4,
    "image_url": "uploads/user_1/item_4_jkl012.jpg"
  }
}
```

**정상 응답 - 부분 코디 (200 OK)**
```json
{
  "top": {
    "id": 1,
    "image_url": "uploads/user_1/item_1_abc123.jpg"
  },
  "bottom": null,
  "shoes": null,
  "outer": null
}
```

**정상 응답 - 빈 코디 (200 OK)**
```json
{
  "top": null,
  "bottom": null,
  "shoes": null,
  "outer": null
}
```

#### `PUT /api/v1/outfit/today`

**정상 응답 (200 OK)**
```json
{
  "message": "top 변경 완료"
}
```

**비정상 응답 (400 Bad Request)**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "잘못된 카테고리입니다. 가능한 값: top, bottom, shoes, outer",
  "detail": {
    "category": "잘못된카테고리"
  }
}
```

**비정상 응답 (404 Not Found) - 아이템을 찾을 수 없음**
```json
{
  "status": "error",
  "code": 404,
  "error": "Not Found",
  "message": "해당 카테고리의 아이템을 찾을 수 없습니다.",
  "detail": {
    "resource": "closet_item",
    "item_id": 999,
    "category": "top"
  }
}
```

#### `PUT /api/v1/outfit/clear`

**정상 응답 (200 OK)**
```json
{
  "message": "top 비우기 완료"
}
```

#### `POST /api/v1/outfit/recommend`

**설명**
- AI 추천 모델(Word2Vec 기반)을 사용하여 사용자의 옷장 아이템 중에서 코디를 추천합니다.
- 현재 선택된 아이템이 있으면 해당 카테고리는 유지하고 나머지 카테고리만 추천합니다.
- `outer`는 선택 사항이므로 추천 결과에 포함되지 않을 수 있습니다.
- 최소한 `top`, `bottom`, `shoes` 카테고리에 각각 하나 이상의 아이템이 있어야 추천이 가능합니다.

**정상 응답 - 완전한 추천 (200 OK)**
```json
{
  "top": {
    "id": 5,
    "image_url": "uploads/user_1/item_5_mno345.jpg"
  },
  "bottom": {
    "id": 6,
    "image_url": "uploads/user_1/item_6_pqr678.jpg"
  },
  "shoes": {
    "id": 7,
    "image_url": "uploads/user_1/item_7_stu901.jpg"
  },
  "outer": {
    "id": 8,
    "image_url": "uploads/user_1/item_8_vwx234.jpg"
  }
}
```

**정상 응답 - 부분 추천 (200 OK)**
*(이미 선택된 아이템이 있는 경우 해당 카테고리는 유지되고 나머지만 추천)*
```json
{
  "top": {
    "id": 1,
    "image_url": "uploads/user_1/item_1_abc123.jpg"
  },
  "bottom": {
    "id": 6,
    "image_url": "uploads/user_1/item_6_pqr678.jpg"
  },
  "shoes": {
    "id": 7,
    "image_url": "uploads/user_1/item_7_stu901.jpg"
  },
  "outer": null
}
```

**정상 응답 - outer 없이 추천 (200 OK)**
*(outer 카테고리에 아이템이 없거나 추천되지 않은 경우)*
```json
{
  "top": {
    "id": 5,
    "image_url": "uploads/user_1/item_5_mno345.jpg"
  },
  "bottom": {
    "id": 6,
    "image_url": "uploads/user_1/item_6_pqr678.jpg"
  },
  "shoes": {
    "id": 7,
    "image_url": "uploads/user_1/item_7_stu901.jpg"
  },
  "outer": null
}
```

**비정상 응답 (404 Not Found) - 옷장에 아이템이 없는 경우**
```json
{
  "status": "error",
  "code": 404,
  "error": "Not Found",
  "message": "옷장에 아이템이 없습니다.",
  "detail": {
    "resource": "closet_items",
    "user_id": 1
  }
}
```

**비정상 응답 (400 Bad Request) - AI 추천 모델을 사용할 수 없는 경우**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "AI 추천 모델을 사용할 수 없습니다. ai_recommendation 모듈이 설치되지 않았습니다.",
  "detail": {}
}
```

**비정상 응답 (400 Bad Request) - AI 추천 모델 로드 실패**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "AI 추천 모델을 로드할 수 없습니다.",
  "detail": {
    "error": "..."
  }
}
```

**비정상 응답 (400 Bad Request) - AI 추천 중 오류 발생**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "AI 추천 중 오류가 발생했습니다.",
  "detail": {
    "error": "..."
  }
}
```

---

### 4. Favorites API

#### `GET /api/v1/favorites`

**정상 응답 (200 OK)**
```json
[
  {
    "id": 1,
    "name": "주말 데일리룩"
  },
  {
    "id": 2,
    "name": "출근 코디"
  }
]
```

**빈 목록 응답 (200 OK)**
```json
[]
```

#### `GET /api/v1/favorites/{id}`

**정상 응답 - outer 포함 (200 OK)**
```json
{
  "name": "주말 데일리룩",
  "top": {
    "id": 1,
    "image_url": "uploads/user_1/item_1_abc123.jpg"
  },
  "bottom": {
    "id": 2,
    "image_url": "uploads/user_1/item_2_def456.jpg"
  },
  "shoes": {
    "id": 3,
    "image_url": "uploads/user_1/item_3_ghi789.jpg"
  },
  "outer": {
    "id": 4,
    "image_url": "uploads/user_1/item_4_jkl012.jpg"
  }
}
```

**정상 응답 - outer 없음 (200 OK)**
*(outer는 선택 사항이므로 null일 수 있음)*
```json
{
  "name": "여름 데일리룩",
  "top": {
    "id": 1,
    "image_url": "uploads/user_1/item_1_abc123.jpg"
  },
  "bottom": {
    "id": 2,
    "image_url": "uploads/user_1/item_2_def456.jpg"
  },
  "shoes": {
    "id": 3,
    "image_url": "uploads/user_1/item_3_ghi789.jpg"
  },
  "outer": null
}
```

**비정상 응답 (404 Not Found)**
```json
{
  "status": "error",
  "code": 404,
  "error": "Not Found",
  "message": "즐겨찾는 코디를 찾을 수 없습니다.",
  "detail": {
    "resource": "favorite_outfit",
    "id": 999
  }
}
```

#### `POST /api/v1/favorites`

**정상 응답 (200 OK)**
```json
{
  "message": "저장 완료"
}
```

**비정상 응답 (400 Bad Request) - 코디가 완성되지 않은 경우**
```json
{
  "status": "error",
  "code": 400,
  "error": "Bad Request",
  "message": "코디를 완성해주세요. (top, bottom, shoes가 모두 선택되어야 합니다)",
  "detail": {
    "today_outfit": {
      "top_id": 1,
      "bottom_id": 2,
      "shoes_id": null,
      "outer_id": null
    }
  }
}
```

**참고**: `outer`는 선택 사항이므로 저장 시 필수로 선택할 필요가 없습니다. `top`, `bottom`, `shoes`만 선택되어 있으면 저장 가능합니다.

**비정상 응답 (409 Conflict) - 중복 이름**
```json
{
  "status": "error",
  "code": 409,
  "error": "Conflict",
  "message": "이미 같은 이름의 즐겨찾는 코디가 있습니다.",
  "detail": {
    "name": "주말 데일리룩"
  }
}
```

#### `PUT /api/v1/favorites/{id}`

**정상 응답 (200 OK)**
```json
{
  "message": "이름이 변경되었습니다."
}
```

**비정상 응답 (404 Not Found)**
```json
{
  "status": "error",
  "code": 404,
  "error": "Not Found",
  "message": "즐겨찾는 코디를 찾을 수 없습니다.",
  "detail": {
    "resource": "favorite_outfit",
    "id": 999
  }
}
```

**비정상 응답 (409 Conflict) - 변경하려는 이름이 이미 존재**
```json
{
  "status": "error",
  "code": 409,
  "error": "Conflict",
  "message": "이미 같은 이름의 즐겨찾는 코디가 있습니다.",
  "detail": {
    "name": "주말 데일리룩"
  }
}
```

#### `DELETE /api/v1/favorites/{id}`

**정상 응답 (200 OK)**
```json
{
  "message": "삭제 완료"
}
```

**비정상 응답 (404 Not Found)**
```json
{
  "status": "error",
  "code": 404,
  "error": "Not Found",
  "message": "즐겨찾는 코디를 찾을 수 없습니다.",
  "detail": {
    "resource": "favorite_outfit",
    "id": 999
  }
}
```

---

### 🔐 인증 오류

모든 API에서 인증 토큰이 없거나 잘못된 경우:

**비정상 응답 (401 Unauthorized) - 유효하지 않은 토큰**
```json
{
  "status": "error",
  "code": 401,
  "error": "Unauthorized",
  "message": "유효하지 않은 인증 토큰입니다.",
  "detail": {}
}
```

**비정상 응답 (401 Unauthorized) - 헤더 누락**
```json
{
  "status": "error",
  "code": 401,
  "error": "Unauthorized",
  "message": "인증 토큰이 제공되지 않았습니다.",
  "detail": {
    "header": "Authorization"
  }
}
```

**참고**: 
- Firebase ID 토큰은 `Authorization: Bearer <firebase_id_token>` 형식으로 전송해야 합니다.
- 토큰이 만료되면 클라이언트에서 토큰을 갱신한 후 재시도해야 합니다.

---

### 📝 응답 구조 공통 규칙

1. **정상 응답**: 모든 필드가 포함된 완전한 JSON 객체 또는 배열
2. **빈 값 처리**: 
   - 배열은 빈 배열 `[]`로 반환
   - Optional 필드는 `null`로 반환
   - 예: 코디가 비어있으면 모든 카테고리가 `null`
3. **에러 응답**: 모든 에러는 일관된 구조를 가짐
   ```json
   {
     "status": "error",
     "code": <HTTP 상태 코드>,
     "error": "<에러 타입>",
     "message": "<사용자 친화적 메시지>",
     "detail": { <추가 정보> }
   }
   ```
4. **HTTP 상태 코드**:
   - `200 OK`: 정상 응답
   - `400 Bad Request`: 잘못된 요청 (파라미터 오류 등)
   - `401 Unauthorized`: 인증 실패
   - `404 Not Found`: 리소스를 찾을 수 없음
   - `409 Conflict`: 중복/충돌
   - `500 Internal Server Error`: 서버 내부 오류

