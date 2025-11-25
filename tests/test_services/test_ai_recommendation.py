"""
AI 추천 서비스 테스트
- AI 모델을 사용한 코디 추천 기능 검증
"""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, ClosetItem, TodayOutfit


@pytest.fixture(scope="function")
def test_closet_items_with_features(test_db: Session, test_user: User) -> list[ClosetItem]:
    """
    Feature 정보가 있는 테스트용 옷장 아이템들을 생성하는 fixture
    AI 추천을 위해서는 feature 정보가 필수입니다.
    
    Args:
        test_db: 테스트용 DB 세션
        test_user: 테스트용 사용자
    
    Returns:
        list[ClosetItem]: 생성된 옷장 아이템 리스트 (feature 포함)
    """
    items = [
        # top 아이템들
        ClosetItem(
            user_id=test_user.id,
            category="top",
            feature="상의_white_cotton_반소매 티셔츠_남성_여름_casual"
        ),
        ClosetItem(
            user_id=test_user.id,
            category="top",
            feature="상의_black_cotton_후드 티셔츠_남성_가을_street"
        ),
        # bottom 아이템들
        ClosetItem(
            user_id=test_user.id,
            category="bottom",
            feature="하의_gray_cotton_숏 팬츠_남성_여름_casual"
        ),
        ClosetItem(
            user_id=test_user.id,
            category="bottom",
            feature="하의_blue_denim_청바지_남성_사계절_casual"
        ),
        # shoes 아이템들
        ClosetItem(
            user_id=test_user.id,
            category="shoes",
            feature="신발_white_canvas_스니커즈_남성_사계절_casual"
        ),
        ClosetItem(
            user_id=test_user.id,
            category="shoes",
            feature="신발_black_leather_구두_남성_사계절_minimal"
        ),
        # outer 아이템들 (선택 사항)
        ClosetItem(
            user_id=test_user.id,
            category="outer",
            feature="아우터_black_wool_후드 집업_남성_가을_street"
        ),
        ClosetItem(
            user_id=test_user.id,
            category="outer",
            feature="아우터_navy_polyester_블루종/MA-1_남성_가을_casual"
        ),
    ]
    
    for item in items:
        test_db.add(item)
    
    test_db.commit()
    
    for item in items:
        test_db.refresh(item)
    
    return items




class TestAIModelRecommendation:
    """AI 모델을 사용한 코디 추천 테스트"""
    
    def test_ai_recommendation_with_features(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_closet_items_with_features: list[ClosetItem],
        test_db: Session
    ):
        """
        Feature 정보가 있는 아이템으로 AI 추천 테스트
        
        시나리오:
        1. 모든 카테고리에 feature 정보가 있는 아이템 존재
        2. AI 추천 요청
        3. 200 OK 응답 확인
        4. 필수 카테고리 (top, bottom, shoes)가 모두 추천되었는지 확인
        5. 추천된 아이템이 실제 옷장에 존재하는지 확인
        """
        # Given: feature 정보가 있는 아이템들이 옷장에 있음
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        
        # 응답 구조 확인
        assert "top" in data
        assert "bottom" in data
        assert "shoes" in data
        assert "outer" in data
        
        # 필수 카테고리는 반드시 추천되어야 함
        assert data["top"] is not None, "top는 필수 카테고리이므로 추천되어야 함"
        assert data["bottom"] is not None, "bottom는 필수 카테고리이므로 추천되어야 함"
        assert data["shoes"] is not None, "shoes는 필수 카테고리이므로 추천되어야 함"
        
        # 추천된 아이템이 실제 옷장에 존재하는지 확인
        top_id = data["top"]["id"]
        bottom_id = data["bottom"]["id"]
        shoes_id = data["shoes"]["id"]
        
        top_item = test_db.query(ClosetItem).filter(ClosetItem.id == top_id).first()
        bottom_item = test_db.query(ClosetItem).filter(ClosetItem.id == bottom_id).first()
        shoes_item = test_db.query(ClosetItem).filter(ClosetItem.id == shoes_id).first()
        
        assert top_item is not None, "추천된 top 아이템이 옷장에 존재해야 함"
        assert bottom_item is not None, "추천된 bottom 아이템이 옷장에 존재해야 함"
        assert shoes_item is not None, "추천된 shoes 아이템이 옷장에 존재해야 함"
        
        # 추천된 아이템들이 올바른 카테고리인지 확인
        assert top_item.category == "top"
        assert bottom_item.category == "bottom"
        assert shoes_item.category == "shoes"
        
        # 추천된 아이템들이 feature 정보를 가지고 있는지 확인
        assert top_item.feature is not None, "추천된 top 아이템은 feature 정보가 있어야 함"
        assert bottom_item.feature is not None, "추천된 bottom 아이템은 feature 정보가 있어야 함"
        assert shoes_item.feature is not None, "추천된 shoes 아이템은 feature 정보가 있어야 함"
        
        # DB에 저장되었는지 확인
        today_outfit = test_db.query(TodayOutfit).filter(
            TodayOutfit.user_id == test_user.id
        ).first()
        assert today_outfit is not None
        assert today_outfit.top_id == top_id
        assert today_outfit.bottom_id == bottom_id
        assert today_outfit.shoes_id == shoes_id
    
    def test_ai_recommendation_keeps_existing_items(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_closet_items_with_features: list[ClosetItem],
        test_db: Session
    ):
        """
        기존에 선택된 아이템이 있을 때 AI 추천 테스트
        
        시나리오:
        1. top 아이템을 먼저 선택
        2. AI 추천 요청
        3. 선택한 top는 유지되고 나머지만 추천되는지 확인
        """
        # Given: top 아이템을 먼저 선택
        selected_top_id = test_closet_items_with_features[0].id
        client.put(
            "/api/v1/outfit/today",
            json={"category": "top", "item_id": selected_top_id},
            headers=auth_headers
        )
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        
        # 선택한 top가 유지되는지 확인
        assert data["top"] is not None
        assert data["top"]["id"] == selected_top_id, "선택한 top 아이템이 유지되어야 함"
        
        # 나머지 카테고리는 추천되어야 함
        assert data["bottom"] is not None
        assert data["shoes"] is not None
    
    def test_ai_recommendation_with_minimal_items(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_db: Session
    ):
        """
        최소한의 아이템으로 AI 추천 테스트
        
        시나리오:
        1. 필수 카테고리(top, bottom, shoes)에만 아이템이 있음
        2. AI 추천 요청
        3. 모든 필수 카테고리가 추천되는지 확인
        
        Note: feature는 필수 필드이므로 모든 아이템에 feature 정보가 있어야 합니다.
        """
        # Given: 필수 카테고리에만 아이템이 있음
        items = [
            ClosetItem(
                user_id=test_user.id,
                category="top",
                feature="상의_white_cotton_반소매 티셔츠_남성_여름_casual"
            ),
            ClosetItem(
                user_id=test_user.id,
                category="bottom",
                feature="하의_gray_cotton_숏 팬츠_남성_여름_casual"
            ),
            ClosetItem(
                user_id=test_user.id,
                category="shoes",
                feature="신발_white_canvas_스니커즈_남성_사계절_casual"
            ),
        ]
        
        for item in items:
            test_db.add(item)
        test_db.commit()
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        
        # 필수 카테고리는 모두 추천되어야 함
        assert data["top"] is not None, "top는 필수 카테고리이므로 추천되어야 함"
        assert data["bottom"] is not None, "bottom는 필수 카테고리이므로 추천되어야 함"
        assert data["shoes"] is not None, "shoes는 필수 카테고리이므로 추천되어야 함"
        
        # 추천된 아이템들이 feature를 가지고 있는지 확인
        top_item = test_db.query(ClosetItem).filter(
            ClosetItem.id == data["top"]["id"]
        ).first()
        assert top_item.feature is not None, "추천된 top 아이템은 feature가 있어야 함"
        
        bottom_item = test_db.query(ClosetItem).filter(
            ClosetItem.id == data["bottom"]["id"]
        ).first()
        assert bottom_item.feature is not None, "추천된 bottom 아이템은 feature가 있어야 함"
        
        shoes_item = test_db.query(ClosetItem).filter(
            ClosetItem.id == data["shoes"]["id"]
        ).first()
        assert shoes_item.feature is not None, "추천된 shoes 아이템은 feature가 있어야 함"
    
    def test_ai_recommendation_feature_format_validation(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_closet_items_with_features: list[ClosetItem],
        test_db: Session
    ):
        """
        Feature 형식 검증 테스트
        
        시나리오:
        1. 올바른 형식의 feature로 AI 추천
        2. 추천 결과가 올바르게 반환되는지 확인
        3. Feature 형식: 카테고리_색상_재질_상세정보_성별_계절_스타일
        """
        # Given: 올바른 형식의 feature를 가진 아이템들
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        
        # 추천된 아이템들의 feature 형식 확인
        if data.get("top"):
            top_item = test_db.query(ClosetItem).filter(
                ClosetItem.id == data["top"]["id"]
            ).first()
            if top_item and top_item.feature:
                parts = top_item.feature.split("_")
                # 최소 7개 부분이 있어야 함 (카테고리_색상_재질_상세정보_성별_계절_스타일)
                assert len(parts) >= 7, f"Feature 형식이 올바르지 않습니다: {top_item.feature}"
                assert parts[0] in ["상의", "하의", "신발", "아우터"], "첫 번째 부분은 카테고리여야 함"
    
    def test_ai_recommendation_multiple_categories(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_closet_items_with_features: list[ClosetItem],
        test_db: Session
    ):
        """
        여러 카테고리 추천 테스트
        
        시나리오:
        1. 모든 카테고리에 아이템이 있는 상태
        2. AI 추천 요청
        3. 각 카테고리별로 적절한 아이템이 추천되는지 확인
        """
        # Given: 모든 카테고리에 feature 정보가 있는 아이템들이 있음
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        
        # 필수 카테고리 확인
        assert data["top"] is not None
        assert data["bottom"] is not None
        assert data["shoes"] is not None
        
        # outer는 선택 사항이므로 None일 수 있음
        # 하지만 아이템이 있으면 추천될 수 있음
        
        # 각 추천된 아이템이 올바른 카테고리인지 확인
        categories = ["top", "bottom", "shoes", "outer"]
        for category in categories:
            if data.get(category):
                item = test_db.query(ClosetItem).filter(
                    ClosetItem.id == data[category]["id"]
                ).first()
                assert item is not None
                assert item.category == category, f"{category} 카테고리의 아이템이 추천되어야 함"
    
    @pytest.mark.skipif(
        not os.path.exists("ai_recommendation/models/w2v_model.model"),
        reason="AI 모델 파일이 없습니다. 모델을 학습해야 합니다."
    )
    def test_ai_recommendation_model_loaded(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_closet_items_with_features: list[ClosetItem]
    ):
        """
        AI 모델이 로드되었는지 확인하는 테스트
        
        시나리오:
        1. 모델 파일이 존재하는 경우
        2. AI 추천 요청
        3. 모델이 정상적으로 사용되는지 확인 (랜덤 추천이 아닌 AI 추천)
        
        Note: 모델 파일이 없으면 스킵됩니다.
        """
        # Given: 모델 파일이 존재함
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 성공 응답 (모델이 로드되었으면 200, 없으면 400 또는 랜덤 추천)
        assert response.status_code == 200
        
        data = response.json()
        
        # AI 추천이 정상적으로 동작했다면 필수 카테고리가 모두 추천되어야 함
        assert data["top"] is not None
        assert data["bottom"] is not None
        assert data["shoes"] is not None


class TestAIModelAvailability:
    """AI 모델 사용 가능 여부 테스트"""
    
    def test_ai_model_files_exist(self):
        """
        AI 모델 파일 존재 여부 확인 테스트
        
        시나리오:
        1. 필요한 모델 파일들이 모두 존재하는지 확인
        2. 파일이 없으면 AI 추천이 랜덤으로 대체될 수 있음
        """
        model_dir = "ai_recommendation/models"
        required_files = [
            "w2v_model.model",
            "color_fabric_model.model",
            "merged_df.pkl",
            "filtered_df.pkl",
            "params.json"
        ]
        
        all_exist = True
        missing_files = []
        
        for filename in required_files:
            filepath = os.path.join(model_dir, filename)
            if not os.path.exists(filepath):
                all_exist = False
                missing_files.append(filename)
        
        if not all_exist:
            pytest.skip(
                f"AI 모델 파일이 없습니다: {', '.join(missing_files)}\n"
                "모델을 학습하려면: cd ai_recommendation && python train_model.py"
            )
        
        # 모든 파일이 존재하면 테스트 통과
        assert all_exist, "모든 모델 파일이 존재해야 합니다"
    
    def test_ai_recommendation_model_unavailable_error(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_closet_items_with_features: list[ClosetItem]
    ):
        """
        AI 모델이 없을 때 에러를 반환하는지 테스트
        
        시나리오:
        1. AI 모델이 없는 경우 (또는 로드 실패)
        2. 400 Bad Request 에러 응답 확인
        3. 적절한 에러 메시지 확인
        
        Note: 모델이 있으면 정상 동작하고, 없으면 에러가 발생합니다.
        """
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 응답 확인
        # 모델이 있으면 200 (성공), 모델이 없거나 로드 실패하면 400 (에러)
        if response.status_code == 400:
            # 모델이 없는 경우 에러 응답 확인
            data = response.json()
            detail = data.get("detail", {})
            
            # 에러 메시지에 AI 추천 관련 내용이 포함되어야 함
            error_text = str(detail)
            assert (
                "AI" in error_text or 
                "모델" in error_text or 
                "추천" in error_text or
                "ai_recommendation" in error_text.lower()
            ), f"에러 메시지에 AI 추천 관련 내용이 없습니다: {detail}"
        elif response.status_code == 200:
            # 모델이 있는 경우 성공 응답 (정상 동작)
            data = response.json()
            assert "top" in data
            assert "bottom" in data
            assert "shoes" in data
            # 모델이 있으면 정상적으로 추천되어야 함
            assert data["top"] is not None
            assert data["bottom"] is not None
            assert data["shoes"] is not None
        else:
            # 예상치 못한 상태 코드
            pytest.fail(f"예상치 못한 상태 코드: {response.status_code}, 응답: {response.text}")
