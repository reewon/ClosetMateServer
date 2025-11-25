# 📁 서버용 AI 추천 모듈 - 디렉터리 구조 요약

## 🎯 목적

서버에서 사용할 AI 추천 모델을 독립적인 모듈로 구성했습니다.
학습과 추론을 분리하여 서버 성능을 최적화합니다.

## 📂 최종 디렉터리 구조

```
ai_recommendation/
├── __init__.py                      # 패키지 초기화
├── README.md                        # 메인 문서
├── SETUP.md                         # 설정 가이드
├── STRUCTURE_SUMMARY.md             # 이 파일 (디렉터리 구조 요약)
│
├── train_model.py                   # ⚙️ 모델 학습 스크립트
├── model_loader.py                  # 🔄 모델 로드 모듈
├── recommendation_engine.py        # 🎯 추천 엔진 (구현 예정)
│
├── data/                            # 📊 학습 데이터
│   ├── sentence_comb_fin.csv        # 필수: 코디 문장 데이터
│   └── total_final_data.csv        # 필수: 상품 카테고리 데이터
│
├── models/                          # 🤖 학습된 모델 (자동 생성)
│   ├── w2v_model.model
│   ├── color_fabric_model.model
│   ├── merged_df.pkl
│   ├── filtered_df.pkl
│   └── params.json
│
└── examples/                        # 📚 사용 예시
    └── example_usage.py
```

## 🔄 사용 흐름

### 1️⃣ 초기 설정 (한 번만)
```
1. CSV 파일을 data/ 디렉터리에 복사
2. python train_model.py 실행
3. models/ 디렉터리에 모델 생성됨
```

### 2️⃣ 서버 통합
```
1. 서버 시작 시: model_loader.get_model_loader() 호출
2. API 요청 시: recommendation_engine.recommend_outfit() 호출
```

## 📋 파일 역할

| 파일/디렉터리 | 역할 | 실행 시점 |
|--------------|------|----------|
| `train_model.py` | 모델 학습 및 저장 | 서버 배포 전 (한 번만) |
| `model_loader.py` | 저장된 모델 로드 | 서버 시작 시 |
| `recommendation_engine.py` | 추천 로직 실행 | API 요청 시 |
| `data/*.csv` | 학습 데이터 | 모델 학습 시 읽기 |
| `models/*` | 학습된 모델 | 서버 실행 시 로드 |

## ⚠️ 중요 사항

1. **CSV 파일 필수**: `data/` 디렉터리에 반드시 CSV 파일이 있어야 합니다.
2. **모델 파일**: `models/` 디렉터리는 `.gitignore`에 포함되어 있습니다.
3. **경로**: 모든 경로는 상대 경로로 설정되어 있어 실행 위치가 중요합니다.

## 🚀 빠른 시작

```bash

# 1. 모델 학습
cd ai_recommendation
python train_model.py

# 2. 서버에서 사용
from ai_recommendation.model_loader import get_model_loader
model_loader = get_model_loader()
```

## 📖 관련 문서

- `README.md`: 전체 사용 가이드
- `SETUP.md`: 초기 설정 방법

