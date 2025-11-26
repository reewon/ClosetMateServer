## **Phase 1: 서버 Firebase Auth 구현 및 검증**

### 1단계: Firebase 프로젝트 설정

- Firebase Console에서 프로젝트 생성
- Authentication 활성화
- 이메일/비밀번호 로그인 방법 활성화
- 서비스 계정 키 다운로드 (firebase-service-account.json)
- **주의**: 서비스 계정 키는 절대 Git에 커밋하지 않기 (이미 .gitignore에 포함됨)

### 2단계: 서버 의존성 추가

- requirements.txt에 `firebase-admin>=6.0.0` 추가
- 설치: `pip install firebase-admin`
- 기존 `auth_stub.py`는 유지 (테스트용, 추후 제거 예정)

### 3단계: 서버 Firebase 초기화

- `app/core/firebase.py` 생성
- Firebase Admin SDK 초기화
  - 서비스 계정 키 파일 경로 또는 환경 변수 사용
  - 초기화 실패 시 에러 처리 및 로깅
- `verify_firebase_token()` 함수 구현
  - ID 토큰 검증
  - 토큰 만료, 서명 오류 등 예외 처리
  - 검증 실패 시 로깅

### 4단계: 서버 인증 미들웨어 생성

- `app/utils/auth_firebase.py` 생성
- `verify_firebase_auth()` 의존성 함수 구현
  - Authorization 헤더에서 Bearer 토큰 추출
  - `verify_firebase_token()` 호출
  - 토큰에서 Firebase UID, 이메일 추출
  - 반환 형식: `{"firebase_uid": str, "email": str}`

### 5단계: User 모델 수정

- `app/models/user.py` 수정
- **컬럼 추가/수정**:
  - `firebase_uid`: `Column(String, unique=True, index=True, nullable=False)` - Firebase UID (고유 식별자)
  - `email`: `Column(String, unique=True, index=True, nullable=False)` - 이메일 (로그인 ID 역할)
  - `username`: `Column(String, nullable=False)` - 사용자명 (unique 제거, email이 고유 식별자)
  - `gender`: `Column(String, nullable=False, default="남성")` - 성별 (회원가입 시 사용자로부터 받음)
  - `password`: **제거** (Firebase에서 관리)
- **주의사항**:
  - 아이디 역할이 `username`에서 `email`로 변경됨
  - 모든 라우터에서 사용자 조회 시 `email` 또는 `firebase_uid` 사용
  - 기존 `username` 기반 코드 수정 필요

### 6단계: Dependencies 수정

- `app/utils/dependencies.py` 수정
- `get_current_user()` 함수 수정:
  - `verify_firebase_auth()` 의존성 사용 (기존 `verify_test_token` 대체)
  - Firebase UID로 사용자 조회
  - **사용자가 없으면 자동 생성**:
    - Firebase 토큰에서 `email` 추출
    - `username`: 기본값 `"user_{firebase_uid[:8]}"` 사용 (나중에 `/auth/sync`로 업데이트)
    - `gender`: 기본값 `"남성"` 사용 (나중에 `/auth/sync`로 업데이트)
    - 첫 API 호출 시 자동 생성 후, 회원가입 완료 시 `/auth/sync` 엔드포인트로 사용자 정보 동기화
  - 사용자 생성/조회 실패 시 예외 처리 및 로깅

### 7단계: Config 및 Main 수정

- `app/core/config.py`에 Firebase 설정 추가 (3단계에서 이미 완료):
  ```python
  FIREBASE_CREDENTIALS_PATH: Optional[str] = None  # 서비스 계정 키 파일 경로
  ```
  - 환경 변수로 관리 (`.env` 파일)
- `app/main.py`에서 Firebase 초기화:
  - 앱 시작 시 `firebase.py`의 `initialize_firebase()` 함수 호출
  - `on_startup` 이벤트에 추가
  - 초기화 실패 시 앱 시작 중단 및 에러 로깅

### 8단계: Auth Router 추가 (필수)

- `app/routers/auth_router.py` 수정/확장
- 엔드포인트 추가:
  - `GET /auth/me`: 현재 사용자 정보 조회
    - `get_current_user()` 의존성 사용
    - 사용자 정보 반환 (id, firebase_uid, email, username, gender)
  - `POST /auth/sync`: 사용자 정보 동기화 (회원가입 후 username, gender 업데이트)
    - 요청 본문: `{"username": str, "gender": str}`
    - Firebase UID로 사용자 찾아서 업데이트
    - **참고**: 사용자는 이미 `get_current_user()`에서 자동 생성되었을 수 있음

---

## **Phase 2: 서버 테스트 및 검증**

### 9단계: 서버 테스트 도구 생성

- `scripts/test_firebase_auth.py` 생성 (Python 스크립트 권장)
- **방법**: Firebase Console에서 수동으로 테스트 사용자 생성
- **주의**: Firebase Admin SDK로는 ID 토큰을 생성할 수 없음 (클라이언트에서만 생성 가능)

### 10단계: 서버 API 테스트

- Postman/curl로 서버 API 테스트:
    
    ```bash
    # 테스트 사용자 생성 (Firebase Console에서 수동 생성)
    # ID 토큰 획득 (웹 페이지 또는 Flutter 앱)
    
    # 서버 API 호출 테스트
    curl -X GET http://127.0.0.1:8000/api/v1/closet/items \
      -H "Authorization: Bearer <firebase_id_token>"
    
    # 사용자 정보 동기화 테스트
    curl -X POST http://127.0.0.1:8000/api/v1/auth/sync \
      -H "Authorization: Bearer <firebase_id_token>" \
      -H "Content-Type: application/json" \
      -d '{"username": "testuser", "gender": "남성"}'
    ```
    
- **검증 항목**:
  - 토큰 검증 정상 동작
  - 사용자 자동 생성/조회
  - 인증 실패 시 401 응답
  - 토큰 만료 처리
  - 잘못된 토큰 형식 처리
  - 토큰 검증 실패 시 로깅 확인

### 11단계: 데이터베이스 마이그레이션 (SQLite - 임시) ✅ 완료

- **참고**: 이 단계는 SQLite에서 Firebase Auth 구조를 테스트하기 위한 임시 마이그레이션입니다.
- **Phase 3에서 PostgreSQL로 마이그레이션할 예정**이므로, 이 단계는 개발/테스트 목적입니다.
- 기존 User 테이블에 Firebase 관련 컬럼 추가 및 `password` 컬럼 제거
- **실행 방법**: 수동 스크립트 사용
  - `scripts/migrate_user_table.py`: 컬럼 추가 (firebase_uid, email)
  - `scripts/recreate_user_table.py`: 테이블 재생성 (password 컬럼 완전 제거)
  - 실행 결과:
    - ✅ `firebase_uid` 컬럼 추가됨 (UNIQUE, NOT NULL)
    - ✅ `email` 컬럼 추가됨 (UNIQUE, NOT NULL)
    - ✅ `password` 컬럼 제거됨
    - ✅ 인덱스 생성됨 (firebase_uid, email)
- **주의**: 기존 테스트 데이터 백업 후 진행 (백업 파일: `closet.db.backup`)

---

## **Phase 3: PostgreSQL 마이그레이션 (서버 인프라 완성)**

### 12단계: PostgreSQL 데이터베이스 설정

- PostgreSQL 설치 및 데이터베이스 생성
- 연결 정보 확인:
  - 호스트, 포트, 데이터베이스명
  - 사용자명, 비밀번호
- **주의**: 개발/프로덕션 환경 분리

### 13단계: 의존성 추가

- `requirements.txt`에 `psycopg2-binary>=2.9.0` 또는 `asyncpg` 추가
- 설치: `pip install psycopg2-binary`

### 14단계: Config 수정

- `app/core/config.py` 수정:
  - `DATABASE_URL`을 PostgreSQL 연결 문자열로 변경
  - 형식: `postgresql://user:password@host:port/database`
  - 환경 변수로 관리 (`.env` 파일)
  - SQLite 기본값 제거 또는 개발 환경에서만 사용

### 15단계: 데이터베이스 마이그레이션

- **기존 SQLite 데이터 백업** (필요 시):
  - SQLite 데이터베이스 파일 백업
  - 또는 데이터 덤프
- **Alembic 사용 (권장)**:
  - Alembic이 이미 설정되어 있다면 마이그레이션 생성
  - `alembic revision --autogenerate -m "migrate_to_postgresql"`
  - PostgreSQL 스키마 생성: `alembic upgrade head`
- **수동 마이그레이션**:
  - PostgreSQL에서 스키마 생성
  - SQLite에서 데이터 추출 후 PostgreSQL로 이관 (필요 시)
- **주의사항**:
  - User 테이블의 `firebase_uid`, `email` unique 제약조건 확인
  - 인덱스 생성 확인
  - 외래 키 제약조건 확인

### 16단계: 연결 테스트

- 서버 시작 후 PostgreSQL 연결 확인
- 기존 API 엔드포인트 테스트:
  - 인증이 필요한 모든 엔드포인트 테스트
  - 데이터 CRUD 작업 테스트
  - 트랜잭션 테스트

### 17단계: 성능 및 안정성 검증

- **연결 풀 설정** (SQLAlchemy):
  - `pool_size`, `max_overflow` 등 설정
- **트랜잭션 테스트**:
  - 동시 요청 처리
  - 롤백 테스트
- **에러 처리**:
  - 연결 실패 시 재시도 로직
  - 연결 끊김 처리

### 18단계: 프로덕션 배포 준비

- 환경 변수 설정 (프로덕션)
- 데이터베이스 백업 전략 수립
- 마이그레이션 스크립트 문서화
- 롤백 계획 수립

---

## **Phase 4: Flutter 클라이언트 구현(사실상 앱 완성)**

### 19단계: Flutter 프로젝트 설정

- Flutter 프로젝트 생성 (또는 기존 프로젝트 준비)
- `pubspec.yaml`에 Firebase 패키지 추가:
    
    ```yaml
    dependencies:
      firebase_core: ^2.24.0
      firebase_auth: ^4.15.0
      http: ^1.1.0  # 또는 dio
    ```

### 20단계: Firebase Flutter 설정

- `flutterfire configure` 실행
- `lib/firebase_options.dart` 생성 확인
- `lib/main.dart`에서 Firebase 초기화

### 21단계: Firebase 설정 정보 관리

- `lib/utils/firebase_config.dart` (필요 시)
- 또는 `firebase_options.dart` 직접 사용

### 22단계: 인증 서비스 레이어 생성

- `lib/services/auth_service.dart` 생성
- **함수 구현**:
  - `signUpWithEmail(email, password, username, gender)`: 회원가입
    - Firebase 회원가입 성공 후 **서버 API 호출 필수** (`/auth/sync`)
    - 서버에 username, gender 전송
  - `signInWithEmail(email, password)`: 로그인
  - `signOut()`: 로그아웃
  - `getIdToken(forceRefresh: bool)`: ID 토큰 획득
    - `forceRefresh: true`로 토큰 강제 갱신 가능
  - `getCurrentUser()`: 현재 사용자 정보
  - `authStateChanges()`: 인증 상태 스트림 (Stream)
- **에러 처리**: Firebase Auth 예외를 사용자 친화적 메시지로 변환

### 23단계: 입력 유효성 검증 유틸리티

- `lib/utils/validation.dart` 생성
- `isValidEmail()`
- `isValidPassword()`
- `isValidUsername()`
- `isValidGender()` (남/여 검증)

### 24단계: 토큰 관리 및 저장소

- **참고**: Firebase Auth는 토큰을 자동으로 관리하므로 별도 저장소가 필수는 아님
- **선택 사항**: `lib/utils/token_storage.dart` 생성 (필요 시)
  - SharedPreferences 사용
  - 토큰 저장/로드 (캐싱 목적)
  - **주의**: Firebase Auth의 `getIdToken()`을 직접 사용하는 것이 더 안전함
- **토큰 자동 갱신**: Firebase Auth가 자동 처리 (별도 구현 불필요)

### 25단계: API 클라이언트 생성

- `lib/services/api_service.dart` 생성
- **기능 구현**:
  - `AuthService`에서 토큰 가져오기
  - `Authorization: Bearer <token>` 헤더 자동 추가
  - **토큰 자동 갱신**:
    - Firebase Auth는 토큰 만료 전 자동 갱신
    - `currentUser?.getIdToken(forceRefresh: true)` 사용
    - 401 응답 시 토큰 갱신 후 재시도
  - **에러 처리**:
    - 401 응답 시 재로그인 유도
    - 네트워크 오류 처리
    - 타임아웃 처리

### 26단계: 회원가입 화면 구현

- `lib/screens/signup_screen.dart` 생성
- **입력 필드**: email, password, username, gender (드롭다운 또는 라디오 버튼)
- **유효성 검증**:
  - 이메일 형식 검증
  - 비밀번호 강도 검증 (최소 6자)
  - 사용자명 검증
  - 성별 선택 필수
- **프로세스**:
  1. Firebase 회원가입 호출
  2. **성공 시 서버에 사용자 정보 동기화 필수** (`/auth/sync` API 호출)
  3. username, gender 전송
  4. 동기화 실패 시 에러 처리 (Firebase 사용자는 생성되었지만 서버 동기화 실패)
- **에러 처리 및 사용자 피드백**:
  - 로딩 상태 표시
  - 성공/실패 메시지 표시
  - 네트워크 오류 처리

### 27단계: 로그인 화면 구현

- `lib/screens/login_screen.dart` 생성
- **입력 필드**: email, password
- **기능**:
  - 로그인 버튼
  - 회원가입 화면으로 이동 링크
- **에러 처리**:
  - 잘못된 이메일/비밀번호 처리
  - 네트워크 오류 처리
  - 로딩 상태 표시

### 28단계: 인증 상태 관리

- `lib/providers/auth_provider.dart` 또는 `lib/services/auth_state.dart` 생성
- **기능**:
  - 전역 인증 상태 관리 (로그인/로그아웃)
  - `authStateChanges()` 스트림 구독
  - 현재 사용자 정보 관리
- **라우팅 제어**:
  - 로그인 필요 화면 접근 시 자동 리다이렉트
  - 로그인 상태에 따른 화면 전환

### 29단계: 메인 앱 구조 수정

- `lib/main.dart` 수정
- 인증 상태에 따른 라우팅
- 로그인되지 않은 경우: 로그인/회원가입 화면
- 로그인된 경우: 메인 화면

### 30단계: 에러 처리 및 사용자 경험 개선

- **Firebase Auth 예외 처리** (상세):
  - `email-already-in-use` → "이미 사용 중인 이메일입니다"
  - `weak-password` → "비밀번호는 6자 이상이어야 합니다"
  - `invalid-email` → "올바른 이메일 형식이 아닙니다"
  - `user-not-found` → "등록되지 않은 사용자입니다"
  - `wrong-password` → "비밀번호가 올바르지 않습니다"
  - `network-request-failed` → "네트워크 오류가 발생했습니다"
  - `too-many-requests` → "너무 많은 요청이 발생했습니다. 잠시 후 다시 시도해주세요"
- **사용자 친화적 메시지**: 기술적 에러 코드를 일반 사용자가 이해할 수 있는 메시지로 변환
- **네트워크 오류 처리**: 재시도 로직 또는 사용자에게 재시도 안내
- **로딩 상태 표시**: 버튼 비활성화, 로딩 인디케이터 표시

### 31단계: 서버 동기화 (필수)

- **회원가입 성공 후 서버 API 호출 필수**
- `/auth/sync` 엔드포인트 호출
- **전송 데이터**: `{"username": str, "gender": str}`
- **에러 처리**:
  - 서버 동기화 실패 시 Firebase 사용자는 이미 생성됨
  - 재시도 로직 또는 사용자에게 수동 동기화 안내
- **대안**: 서버에서 첫 API 호출 시 Firebase UID로 자동 생성
  - 하지만 username, gender는 별도로 받아야 하므로 `/auth/sync` 호출 권장

---

## **Phase 5: 통합 테스트 및 최종 검증**

### 32단계: 통합 테스트

- Flutter 앱에서 회원가입 → 서버 API 호출 테스트
- 로그인 → 서버 API 호출 테스트
- 토큰 자동 갱신 테스트
- 로그아웃 테스트
- PostgreSQL 데이터베이스와의 연동 확인

### 33단계: 에러 시나리오 테스트

- **입력 검증 테스트**:
  - 잘못된 이메일 형식
  - 약한 비밀번호 (6자 미만)
  - 빈 필드 (email, password, username, gender)
- **인증 테스트**:
  - 중복 이메일 회원가입 시도
  - 잘못된 로그인 정보 (존재하지 않는 이메일)
  - 잘못된 비밀번호
- **네트워크 및 토큰 테스트**:
  - 네트워크 오류 상황
  - 토큰 만료 시나리오
  - 잘못된 토큰 형식
  - 서버 동기화 실패 시나리오
- **데이터베이스 테스트**:
  - PostgreSQL 연결 실패 시나리오
  - 동시성 테스트

### 34단계: 보안 검토

- **.gitignore 확인** (이미 포함되어 있음):
  - `firebase-service-account.json` 또는 `*service-account*.json`
  - `.env` (서버)
  - 토큰 저장 파일 (클라이언트)
- **환경 변수 관리**:
  - 프로덕션/개발 환경 분리
  - 민감한 정보는 환경 변수로 관리
- **HTTPS 사용**: 프로덕션 환경에서는 반드시 HTTPS 사용
- **토큰 보안**:
  - 클라이언트에서 토큰 안전하게 저장 (SharedPreferences 암호화 고려)
  - 토큰 만료 시간 확인
  - 리프레시 토큰 관리 (Firebase Auth 자동 처리)
- **데이터베이스 보안**:
  - PostgreSQL 연결 문자열 보안 관리
  - 데이터베이스 접근 권한 설정