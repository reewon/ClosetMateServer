"""
오늘의 코디 라우터 테스트
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, ClosetItem, TodayOutfit


class TestGetTodayOutfit:
    """오늘의 코디 조회 테스트"""
    
    def test_get_today_outfit_empty(self, client: TestClient, auth_headers: dict, test_user: User):
        """
        빈 오늘의 코디 조회 테스트 (자동 생성)
        
        시나리오:
        1. 오늘의 코디가 없는 상태에서 조회
        2. 200 OK 응답 확인
        3. 모든 카테고리가 null인 코디 반환 확인
        """
        # Given: 오늘의 코디가 없음 (자동 생성됨)
        
        # When: 오늘의 코디 조회
        response = client.get("/api/v1/outfit/today", headers=auth_headers)
        
        # Then: 빈 코디 반환
        assert response.status_code == 200
        
        data = response.json()
        assert data["top"] is None
        assert data["bottom"] is None
        assert data["shoes"] is None
        assert data["outer"] is None
    
    def test_get_today_outfit_with_items(self, client: TestClient, auth_headers: dict,
                                        test_user: User, test_today_outfit: TodayOutfit,
                                        test_closet_items: list[ClosetItem]):
        """
        코디가 설정된 상태에서 조회 테스트
        
        시나리오:
        1. 오늘의 코디에 아이템이 설정된 상태
        2. 200 OK 응답 확인
        3. 모든 아이템 정보가 올바르게 반환되는지 확인
        """
        # Given: test_today_outfit에 아이템 설정됨
        
        # When: 오늘의 코디 조회
        response = client.get("/api/v1/outfit/today", headers=auth_headers)
        
        # Then: 코디 정보 반환
        assert response.status_code == 200
        
        data = response.json()
        
        # 각 카테고리에 아이템이 있는지 확인
        assert data["top"] is not None
        assert data["top"]["id"] == test_closet_items[0].id
        assert data["top"]["name"] == "화이트 티셔츠"
        
        assert data["bottom"] is not None
        assert data["bottom"]["id"] == test_closet_items[2].id
        assert data["bottom"]["name"] == "베이지 팬츠"
        
        assert data["shoes"] is not None
        assert data["shoes"]["id"] == test_closet_items[4].id
        assert data["shoes"]["name"] == "화이트 운동화"
        
        assert data["outer"] is not None
        assert data["outer"]["id"] == test_closet_items[6].id
        assert data["outer"]["name"] == "블루 데님 재킷"
    
    def test_get_today_outfit_partial(self, client: TestClient, auth_headers: dict,
                                     test_user: User, empty_today_outfit: TodayOutfit,
                                     test_closet_items: list[ClosetItem], test_db: Session):
        """
        일부 카테고리만 설정된 코디 조회 테스트
        
        시나리오:
        1. top만 설정된 코디
        2. top만 정보가 있고 나머지는 null 확인
        """
        # Given: top만 설정
        empty_today_outfit.top_id = test_closet_items[0].id
        test_db.commit()
        test_db.refresh(empty_today_outfit)
        
        # When: 오늘의 코디 조회
        response = client.get("/api/v1/outfit/today", headers=auth_headers)
        
        # Then: top만 정보가 있음
        assert response.status_code == 200
        
        data = response.json()
        assert data["top"] is not None
        assert data["top"]["name"] == "화이트 티셔츠"
        assert data["bottom"] is None
        assert data["shoes"] is None
        assert data["outer"] is None
    
    def test_get_today_outfit_unauthorized(self, client: TestClient):
        """
        인증 없이 조회 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 요청
        2. 401 Unauthorized 응답 확인
        """
        # Given: 인증 헤더 없음
        
        # When: 인증 없이 조회
        response = client.get("/api/v1/outfit/today")
        
        # Then: 401 에러 응답
        assert response.status_code == 401


class TestUpdateOutfitItem:
    """코디 아이템 변경 테스트"""
    
    def test_update_outfit_item_success(self, client: TestClient, auth_headers: dict,
                                       test_user: User, test_closet_items: list[ClosetItem],
                                       test_db: Session):
        """
        코디 아이템 변경 성공 테스트
        
        시나리오:
        1. top 아이템 변경
        2. 200 OK 응답 확인
        3. DB에 실제로 변경되었는지 확인
        """
        # Given: 변경할 아이템 데이터
        update_data = {
            "category": "top",
            "item_id": test_closet_items[0].id
        }
        
        # When: top 변경 요청
        response = client.put("/api/v1/outfit/today",
                            json=update_data,
                            headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        assert "top 변경 완료" in data["message"]
        
        # DB에서 확인
        today_outfit = test_db.query(TodayOutfit).filter(
            TodayOutfit.user_id == test_user.id
        ).first()
        assert today_outfit.top_id == test_closet_items[0].id
    
    def test_update_outfit_item_all_categories(self, client: TestClient, auth_headers: dict,
                                              test_user: User, test_closet_items: list[ClosetItem],
                                              test_db: Session):
        """
        모든 카테고리 아이템 변경 테스트
        
        시나리오:
        1. top, bottom, shoes, outer 각각 변경
        2. 모두 성공하는지 확인
        """
        # Given: 각 카테고리별 아이템
        test_items = [
            ("top", test_closet_items[0].id),
            ("bottom", test_closet_items[2].id),
            ("shoes", test_closet_items[4].id),
            ("outer", test_closet_items[6].id)
        ]
        
        for category, item_id in test_items:
            # When: 각 카테고리 변경
            response = client.put("/api/v1/outfit/today",
                                json={"category": category, "item_id": item_id},
                                headers=auth_headers)
            
            # Then: 성공 응답
            assert response.status_code == 200
            assert f"{category} 변경 완료" in response.json()["message"]
        
        # 모든 아이템이 설정되었는지 확인
        today_outfit = test_db.query(TodayOutfit).filter(
            TodayOutfit.user_id == test_user.id
        ).first()
        assert today_outfit.top_id == test_closet_items[0].id
        assert today_outfit.bottom_id == test_closet_items[2].id
        assert today_outfit.shoes_id == test_closet_items[4].id
        assert today_outfit.outer_id == test_closet_items[6].id
    
    def test_update_outfit_item_invalid_category(self, client: TestClient, auth_headers: dict,
                                                 test_user: User, test_closet_items: list[ClosetItem]):
        """
        잘못된 카테고리로 변경 시도 테스트
        
        시나리오:
        1. 존재하지 않는 카테고리로 변경 시도
        2. 400 Bad Request 응답 확인
        """
        # Given: 잘못된 카테고리
        update_data = {
            "category": "잘못된카테고리",
            "item_id": test_closet_items[0].id
        }
        
        # When: 잘못된 카테고리로 변경 시도
        response = client.put("/api/v1/outfit/today",
                            json=update_data,
                            headers=auth_headers)
        
        # Then: 400 에러 응답
        assert response.status_code == 400
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 400
        assert "잘못된 카테고리" in data["message"]
    
    def test_update_outfit_item_not_found(self, client: TestClient, auth_headers: dict,
                                         test_user: User):
        """
        존재하지 않는 아이템으로 변경 시도 테스트
        
        시나리오:
        1. 존재하지 않는 아이템 ID로 변경 시도
        2. 404 Not Found 응답 확인
        """
        # Given: 존재하지 않는 아이템 ID
        update_data = {
            "category": "top",
            "item_id": 99999
        }
        
        # When: 존재하지 않는 아이템으로 변경 시도
        response = client.put("/api/v1/outfit/today",
                            json=update_data,
                            headers=auth_headers)
        
        # Then: 404 에러 응답
        assert response.status_code == 404
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 404
        assert "아이템을 찾을 수 없습니다" in data["message"]
    
    def test_update_outfit_item_wrong_category(self, client: TestClient, auth_headers: dict,
                                               test_user: User, test_closet_items: list[ClosetItem]):
        """
        다른 카테고리의 아이템으로 변경 시도 테스트
        
        시나리오:
        1. top 카테고리에 bottom 아이템 설정 시도
        2. 404 Not Found 응답 확인
        """
        # Given: bottom 아이템을 top에 설정 시도
        update_data = {
            "category": "top",
            "item_id": test_closet_items[2].id  # 베이지 팬츠 (bottom)
        }
        
        # When: 카테고리가 맞지 않는 아이템으로 변경 시도
        response = client.put("/api/v1/outfit/today",
                            json=update_data,
                            headers=auth_headers)
        
        # Then: 404 에러 응답
        assert response.status_code == 404
    
    def test_update_outfit_item_unauthorized(self, client: TestClient,
                                            test_closet_items: list[ClosetItem]):
        """
        인증 없이 변경 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 변경 시도
        2. 401 Unauthorized 응답 확인
        """
        # Given: 변경할 데이터
        update_data = {
            "category": "top",
            "item_id": test_closet_items[0].id
        }
        
        # When: 인증 없이 변경 시도
        response = client.put("/api/v1/outfit/today", json=update_data)
        
        # Then: 401 에러 응답
        assert response.status_code == 401


class TestClearOutfitCategory:
    """코디 카테고리 비우기 테스트"""
    
    def test_clear_outfit_category_success(self, client: TestClient, auth_headers: dict,
                                          test_user: User, test_today_outfit: TodayOutfit,
                                          test_db: Session):
        """
        코디 카테고리 비우기 성공 테스트
        
        시나리오:
        1. top 카테고리 비우기
        2. 200 OK 응답 확인
        3. DB에서 실제로 비워졌는지 확인
        """
        # Given: 오늘의 코디에 아이템이 설정됨
        
        # When: top 비우기 요청
        response = client.put("/api/v1/outfit/clear",
                            json={"category": "top"},
                            headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        assert "top 비우기 완료" in data["message"]
        
        # DB에서 확인 (세션 갱신)
        test_db.expire_all()  # 캐시된 객체 무효화
        today_outfit = test_db.query(TodayOutfit).filter(
            TodayOutfit.user_id == test_user.id
        ).first()
        assert today_outfit.top_id is None
        # 다른 카테고리는 그대로 유지
        assert today_outfit.bottom_id is not None
        assert today_outfit.shoes_id is not None
        assert today_outfit.outer_id is not None
    
    def test_clear_outfit_all_categories(self, client: TestClient, auth_headers: dict,
                                        test_user: User, test_today_outfit: TodayOutfit,
                                        test_db: Session):
        """
        모든 카테고리 비우기 테스트
        
        시나리오:
        1. top, bottom, shoes, outer 각각 비우기
        2. 모두 성공하는지 확인
        """
        # Given: 오늘의 코디에 모든 아이템 설정됨
        categories = ["top", "bottom", "shoes", "outer"]
        
        for category in categories:
            # When: 각 카테고리 비우기
            response = client.put("/api/v1/outfit/clear",
                                json={"category": category},
                                headers=auth_headers)
            
            # Then: 성공 응답
            assert response.status_code == 200
            assert f"{category} 비우기 완료" in response.json()["message"]
        
        # 모든 카테고리가 비워졌는지 확인 (세션 갱신)
        test_db.expire_all()  # 캐시된 객체 무효화
        today_outfit = test_db.query(TodayOutfit).filter(
            TodayOutfit.user_id == test_user.id
        ).first()
        assert today_outfit.top_id is None
        assert today_outfit.bottom_id is None
        assert today_outfit.shoes_id is None
        assert today_outfit.outer_id is None
    
    def test_clear_outfit_invalid_category(self, client: TestClient, auth_headers: dict,
                                          test_user: User):
        """
        잘못된 카테고리 비우기 시도 테스트
        
        시나리오:
        1. 존재하지 않는 카테고리 비우기 시도
        2. 400 Bad Request 응답 확인
        """
        # Given: 잘못된 카테고리
        
        # When: 잘못된 카테고리 비우기 시도
        response = client.put("/api/v1/outfit/clear",
                            json={"category": "잘못된카테고리"},
                            headers=auth_headers)
        
        # Then: 400 에러 응답
        assert response.status_code == 400
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 400
        assert "잘못된 카테고리" in data["message"]
    
    def test_clear_outfit_unauthorized(self, client: TestClient):
        """
        인증 없이 비우기 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 비우기 시도
        2. 401 Unauthorized 응답 확인
        """
        # Given: 인증 헤더 없음
        
        # When: 인증 없이 비우기 시도
        response = client.put("/api/v1/outfit/clear", json={"category": "top"})
        
        # Then: 401 에러 응답
        assert response.status_code == 401


class TestRecommendOutfit:
    """AI 코디 추천 테스트"""
    
    def test_recommend_outfit_success(self, client: TestClient, auth_headers: dict,
                                     test_user: User, test_closet_items: list[ClosetItem],
                                     test_db: Session):
        """
        AI 추천 성공 테스트
        
        시나리오:
        1. 옷장에 아이템이 있는 상태
        2. AI 추천 요청
        3. 200 OK 응답 확인
        4. 추천된 코디가 DB에 저장되었는지 확인
        """
        # Given: 옷장에 아이템들이 있음
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        
        # 각 카테고리에 추천이 있어야 함 (옷장에 아이템이 있으므로)
        # 랜덤이므로 정확한 값은 체크할 수 없지만, 구조는 확인 가능
        assert "top" in data
        assert "bottom" in data
        assert "shoes" in data
        assert "outer" in data
        
        # 최소 하나의 카테고리에는 아이템이 추천되어야 함
        has_recommendation = any([
            data["top"] is not None,
            data["bottom"] is not None,
            data["shoes"] is not None,
            data["outer"] is not None
        ])
        assert has_recommendation
        
        # DB에 저장되었는지 확인
        today_outfit = test_db.query(TodayOutfit).filter(
            TodayOutfit.user_id == test_user.id
        ).first()
        assert today_outfit is not None
    
    def test_recommend_outfit_keeps_existing(self, client: TestClient, auth_headers: dict,
                                            test_user: User, test_closet_items: list[ClosetItem],
                                            test_db: Session):
        """
        기존 아이템 유지 확인 테스트
        
        시나리오:
        1. top를 먼저 선택
        2. AI 추천 요청
        3. 선택한 top는 유지되는지 확인 (AI 추천 로직에서 existing_items 처리)
        """
        # Given: top를 먼저 선택
        client.put("/api/v1/outfit/today",
                  json={"category": "top", "item_id": test_closet_items[0].id},
                  headers=auth_headers)
        
        selected_item_id = test_closet_items[0].id
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        
        # 선택한 top가 유지되는지 확인
        assert data["top"] is not None
        assert data["top"]["id"] == selected_item_id
    
    def test_recommend_outfit_empty_closet(self, client: TestClient, auth_headers: dict,
                                          test_user: User):
        """
        빈 옷장에서 추천 시도 테스트
        
        시나리오:
        1. 옷장에 아이템이 없는 상태
        2. AI 추천 요청
        3. 404 Not Found 응답 확인
        """
        # Given: 옷장에 아이템 없음
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 404 에러 응답
        assert response.status_code == 404
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 404
        assert "옷장에 아이템이 없습니다" in data["message"]
    
    def test_recommend_outfit_partial_closet(self, client: TestClient, auth_headers: dict,
                                            test_user: User, test_db: Session):
        """
        일부 카테고리만 있는 옷장에서 추천 테스트
        
        시나리오:
        1. top만 옷장에 있는 상태
        2. AI 추천 요청
        3. top만 추천되고 나머지는 null인지 확인
        """
        # Given: top 아이템만 추가
        item = ClosetItem(
            user_id=test_user.id,
            category="top",
            name="테스트 상의"
        )
        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)
        
        # When: AI 추천 요청
        response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        
        # top만 추천되고 나머지는 null
        assert data["top"] is not None
        assert data["top"]["name"] == "테스트 상의"
        assert data["bottom"] is None
        assert data["shoes"] is None
        assert data["outer"] is None
    
    def test_recommend_outfit_unauthorized(self, client: TestClient):
        """
        인증 없이 추천 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 추천 요청
        2. 401 Unauthorized 응답 확인
        """
        # Given: 인증 헤더 없음
        
        # When: 인증 없이 추천 요청
        response = client.post("/api/v1/outfit/recommend")
        
        # Then: 401 에러 응답
        assert response.status_code == 401
    
    def test_recommend_outfit_multiple_times(self, client: TestClient, auth_headers: dict,
                                            test_user: User, test_closet_items: list[ClosetItem],
                                            test_db: Session):
        """
        여러 번 추천 요청 테스트
        
        시나리오:
        1. AI 추천을 3번 연속 요청
        2. 모두 성공하는지 확인
        3. 랜덤이므로 결과가 달라질 수 있음을 확인
        """
        # Given: 옷장에 아이템들이 있음
        recommendations = []
        
        for _ in range(3):
            # When: AI 추천 요청
            response = client.post("/api/v1/outfit/recommend", headers=auth_headers)
            
            # Then: 성공 응답
            assert response.status_code == 200
            
            data = response.json()
            recommendations.append(data)
        
        # 모든 추천이 유효한 구조인지 확인
        for rec in recommendations:
            assert "top" in rec
            assert "bottom" in rec
            assert "shoes" in rec
            assert "outer" in rec

