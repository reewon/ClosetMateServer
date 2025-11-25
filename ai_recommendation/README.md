# AI 추천 서비스 - 서버용 모듈

서버에서 사용할 AI 추천 모델 및 엔진입니다.

## 📁 디렉터리 구조

```
ai_recommendation/
├── __init__.py                  # 패키지 초기화
├── README.md                    # 이 파일
├── STRUCTURE_SUMMARY.md         # 디렉터리 구조 요약
├── SETUP.md                     # 설정 가이드
├── train_model.py               # 모델 학습 스크립트
├── model_loader.py              # 모델 로드 모듈
├── recommendation_engine.py      # 추천 엔진 (서버에서 사용, 구현 예정)
├── data/                        # 학습 데이터 (CSV 파일 배치)
│   ├── sentence_comb_fin.csv    # 코디 문장 데이터 (필수)
│   └── total_final_data.csv     # 상품 카테고리 데이터 (필수)
├── models/                      # 학습된 모델 (생성됨, .gitignore)
│   ├── w2v_model.model
│   ├── color_fabric_model.model
│   ├── merged_df.pkl
│   ├── filtered_df.pkl
│   └── params.json
└── examples/                     # 사용 예시
    └── example_usage.py
```

> 📌 **중요**: `data/` 디렉터리에 CSV 파일을 배치해야 합니다!

## 🚀 사용 방법

### 1. 데이터 준비

먼저 `data/` 디렉터리에 CSV 파일을 배치합니다:
- `sentence_comb_fin.csv` (코디 문장 데이터)
- `total_final_data.csv` (상품 카테고리 데이터)

### 2. 모델 학습 (서버 배포 전)

```bash
cd ai_recommendation
python train_model.py
```

이 명령어는:
- `data/` 디렉토리의 CSV 파일을 읽어서 모델 학습
- 학습된 모델을 `models/` 디렉토리에 저장

### 2. 서버에서 사용

```python
from ai_recommendation.model_loader import get_model_loader
from ai_recommendation.recommendation_engine import recommend_outfit

# 서버 시작 시 모델 로드
model_loader = get_model_loader()

# 추천 요청 처리
result = recommend_outfit(
    selected_items=request.selected_items,
    available_items=request.available_items,
    model_loader=model_loader
)
```

## 📋 파일 설명

| 파일 | 용도 | 실행 시점 |
|------|------|----------|
| `train_model.py` | 모델 학습 및 저장 | 서버 배포 전 (한 번만) |
| `model_loader.py` | 저장된 모델 로드 | 서버 시작 시 |
| `recommendation_engine.py` | 추천 로직 실행 | API 요청 시 |
| `data/*.csv` | 학습 데이터 | 모델 학습 시 |
| `models/*` | 학습된 모델 | 서버 실행 시 로드 |

## ⚠️ 주의사항

1. **모델 파일 용량**: `models/` 디렉토리의 파일들은 용량이 클 수 있습니다.
   - `.gitignore`에 추가 권장
   - 서버 배포 시 별도로 전송 필요

2. **데이터 경로**: 
   - `train_model.py`는 `data/` 디렉토리에서 CSV 파일을 읽습니다.
   - 경로가 맞는지 확인하세요.

3. **모델 재학습**:
   - 데이터가 업데이트되면 `train_model.py`를 다시 실행
   - 서버 재시작 시 자동으로 새 모델 로드

## 🔧 설정

`train_model.py`에서 파라미터를 조정할 수 있습니다:

```python
w2v_vector_size = 100      # 문장 임베딩 차원 수
cf_vector_size = 20       # color/fabric 임베딩 차원 수
color_weight = 0.8        # 색상 벡터 가중치
fabric_weight = 0.2      # 재질 벡터 가중치
```

