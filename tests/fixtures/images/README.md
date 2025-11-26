# 테스트용 이미지 파일

이 디렉터리는 Gemini API 통합 테스트를 위한 실제 옷 이미지 파일을 저장합니다.

## 파일 구조

각 카테고리별로 테스트용 이미지를 준비하세요:

- `test_top.jpg` - 상의 테스트용 이미지 (예: 티셔츠, 후드티)
- `test_bottom.jpg` - 하의 테스트용 이미지 (예: 청바지, 슬랙스)
- `test_shoes.jpg` - 신발 테스트용 이미지 (예: 스니커즈, 구두)
- `test_outer.jpg` - 아우터 테스트용 이미지 (예: 재킷, 코트)

## 사용 방법

1. 각 카테고리별로 실제 옷 이미지를 이 디렉터리에 저장
2. 파일명은 위의 형식을 따라야 합니다 (test_{category}.jpg)
3. 이미지가 없어도 Mock 테스트는 정상 동작합니다

## 테스트 실행

### 실제 이미지 통합 테스트 (Gemini API 호출)
```bash
# 실제 이미지 파일을 사용한 통합 테스트
pytest tests/test_routers/test_closet_router.py::TestCreateClosetItemWithRealImage -v
```

## 주의사항

- **실제 Gemini API를 호출**하므로 `.env` 파일에 `GEMINI_API_KEY`가 설정되어 있어야 합니다
- 이미지 파일이 없으면 통합 테스트는 자동으로 스킵됩니다
- 실제 API 호출이므로 테스트 시간이 오래 걸릴 수 있습니다

