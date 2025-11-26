# Firebase Auth 테스트 도구

## 사용 방법

### 1. Firebase Console에서 테스트 사용자 생성

1. [Firebase Console](https://console.firebase.google.com/) 접속
2. 프로젝트 선택 (closetmate-a0b53)
3. 왼쪽 메뉴에서 **Authentication** 클릭
4. 상단 탭에서 **Users** 클릭
5. **Add user** 버튼 클릭
6. 이메일과 비밀번호 입력
   - 예: `test@example.com` / `test123456`
7. **Add user** 클릭하여 생성

### 2. HTML 테스트 도구 사용

1. `test_firebase_auth.html` 파일을 브라우저에서 열기
2. Firebase 설정 추가 필요:
   - Firebase Console → 프로젝트 설정 → 일반 탭
   - 웹 앱의 Firebase 설정 복사
   - `test_firebase_auth.html`의 `firebaseConfig`에 붙여넣기
3. 생성한 사용자의 이메일과 비밀번호로 로그인
4. ID 토큰이 표시되면 복사하여 사용

### 3. 서버 API 테스트

```bash
# ID 토큰을 복사한 후
curl -X GET http://127.0.0.1:8000/api/v1/auth/me \
  -H "Authorization: Bearer <복사한_ID_토큰>"
```

## 주의사항

- Firebase Admin SDK로는 ID 토큰을 생성할 수 없습니다 (클라이언트에서만 생성 가능)
- HTML 파일을 사용하려면 Firebase Web SDK 설정이 필요합니다
- 또는 Flutter 앱에서 로그인 후 ID 토큰을 얻을 수 있습니다

