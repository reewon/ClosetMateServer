# 서버 통합 가이드

서버에서 AI 추천 모듈을 사용하기 위해 필요한 정보입니다.

## 📋 서버에서 필요한 정보

### 1. 모델 로더 인스턴스

서버 시작 시 한 번만 로드합니다:

```python
from ai_recommendation.model_loader import get_model_loader

# 서버 시작 시 (예: FastAPI startup event)
model_loader = get_model_loader()
```

### 2. 추천 엔진 함수

API 요청 시 호출합니다:

```python
from ai_recommendation.recommendation_engine import recommend_outfit

# API 요청 처리 시
result = recommend_outfit(
    selected_items=request.selected_items,
    available_items=request.available_items,
    model_loader=model_loader
)
```

### 3. 요청 데이터 형식

서버에서 AI 모듈로 전달하는 데이터 형식:

```python
{
    "selected_items": {
        "top": {
            "id": 1,
            "feature": "상의_white_cotton_반소매 티셔츠_남성_여름_casual"
        },
        "bottom": null,  # 선택 안 됨
        "shoes": null,   # 선택 안 됨
        "outer": {
            "id": 5,
            "feature": "아우터_black_wool_후드 집업_남성_가을_street"
        }
    },
    "available_items": {
        "bottom": [  # bottom이 None인 경우만 포함
            {
                "id": 2,
                "feature": "하의_gray_cotton_숏 팬츠_남성_여름_casual"
            },
            {
                "id": 3,
                "feature": "하의_blue_denim_청바지_남성_사계절_casual"
            }
        ],
        "shoes": [  # shoes가 None인 경우만 포함
            {
                "id": 4,
                "feature": "신발_white_canvas_스니커즈_남성_사계절_casual"
            }
        ]
    }
}
```

**요청 데이터 설명:**
- `selected_items`: 이미 선택된 아이템 (TodayOutfit에서 None이 아닌 항목)
  - 각 카테고리별로 `{"id": 아이템ID, "feature": "피쳐정보"}` 또는 `null`
- `available_items`: 선택 가능한 아이템 (TodayOutfit에서 None인 카테고리만)
  - 해당 카테고리의 사용자 옷장(ClosetItem) 전체
  - 각 아이템: `{"id": 아이템ID, "feature": "피쳐정보"}`

### 4. 응답 데이터 형식

AI 모듈에서 서버로 반환하는 데이터 형식:

```python
{
    "recommended_outfit": {
        "top": 1,      # 아이템 ID
        "bottom": 2,   # 아이템 ID
        "shoes": 4,    # 아이템 ID
        "outer": 5     # 아이템 ID (또는 null)
    }
}
```

**응답 데이터 설명:**
- `recommended_outfit`: 추천된 코디
  - 각 카테고리별로 아이템 ID 반환
  - `outer`는 선택 사항이므로 `null`일 수 있음
  - **중요**: `top`은 반드시 1개만 추천 (기존 노트북의 1~2개 제한 제거)

## 🔄 전체 흐름

```
1. 서버 시작
   ↓
2. model_loader = get_model_loader()  # 모델 로드
   ↓
3. API 요청 수신
   {
     selected_items: {...},
     available_items: {...}
   }
   ↓
4. recommend_outfit() 호출
   ↓
5. 추천 결과 반환
   {
     recommended_outfit: {
       top: 1,
       bottom: 2,
       shoes: 4,
       outer: 5
     }
   }
```

## 📝 Feature 문자열 형식

`feature` 필드는 다음 형식을 따릅니다:

```
카테고리_색상_재질_상세정보_성별_계절_스타일
```

예시:
- `상의_white_cotton_반소매 티셔츠_남성_여름_casual`
- `하의_gray_cotton_숏 팬츠_남성_여름_casual`
- `신발_white_canvas_스니커즈_남성_사계절_casual`
- `아우터_black_wool_후드 집업_남성_가을_street`

## ⚠️ 주의사항

1. **상의 개수**: 서버에서는 상의를 **1개만** 추천합니다 (기존 노트북의 1~2개 제한 제거)

2. **Feature와 ID 매핑**: 
   - 추천 결과는 `feature` 문자열을 기반으로 계산되지만
   - 최종 응답은 `id`로 반환됩니다
   - `recommendation_engine.py`에서 feature → id 변환 로직 필요

3. **카테고리 제약**:
   - `top`: 필수 1개
   - `bottom`: 필수 1개
   - `shoes`: 필수 1개
   - `outer`: 선택 0~1개

4. **에러 처리**:
   - `available_items`가 비어있는 경우
   - Word2Vec에 없는 토큰 처리
   - 유사도가 너무 낮은 경우

## 🚀 FastAPI 예시

```python
from fastapi import FastAPI
from ai_recommendation.model_loader import get_model_loader
from ai_recommendation.recommendation_engine import recommend_outfit

app = FastAPI()

# 서버 시작 시 모델 로드
@app.on_event("startup")
async def load_models():
    global model_loader
    model_loader = get_model_loader()
    print("✓ 모델 로드 완료")

# API 엔드포인트
@app.post("/recommend")
async def recommend(request_data: dict):
    try:
        result = recommend_outfit(
            selected_items=request_data['selected_items'],
            available_items=request_data['available_items'],
            model_loader=model_loader
        )
        return result
    except Exception as e:
        return {"error": str(e)}
```

## 📦 필요한 파일

서버 배포 시 다음 파일들이 필요합니다:

- `ai_recommendation/model_loader.py` - 모델 로드 모듈
- `ai_recommendation/recommendation_engine.py` - 추천 엔진 (구현 예정)
- `ai_recommendation/models/` - 학습된 모델 디렉터리 (전체)
  - `w2v_model.model`
  - `color_fabric_model.model`
  - `merged_df.pkl`
  - `filtered_df.pkl`
  - `params.json`

**참고**: `train_model.py`와 `data/` 디렉터리는 서버에서 불필요합니다 (학습은 별도로 수행).

