"""
옷장 라우터 테스트
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, ClosetItem


class TestGetClosetItems:
    """옷장 아이템 조회 테스트"""
    
    def test_get_closet_items_success(self, client: TestClient, auth_headers: dict, 
                                     test_user: User, test_closet_items: list[ClosetItem]):
        """
        카테고리별 옷 조회 성공 테스트
        
        시나리오:
        1. top 카테고리 조회
        2. 200 OK 응답 확인
        3. top 2개가 반환되는지 확인
        """
        # Given: test_closet_items에 top 2개 포함됨
        
        # When: top 카테고리 조회
        response = client.get("/api/v1/closet/top", headers=auth_headers)
        
        # Then: 성공 응답 및 데이터 확인
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # top 아이템 확인
        names = [item["name"] for item in data]
        assert "white t-shirt" in names
        assert "black hoodie" in names
        
        # 응답 구조 확인
        for item in data:
            assert "id" in item
            assert "name" in item
            assert isinstance(item["id"], int)
            assert isinstance(item["name"], str)
    
    def test_get_closet_items_empty(self, client: TestClient, auth_headers: dict, test_user: User):
        """
        빈 옷장 조회 테스트
        
        시나리오:
        1. 옷장 아이템이 없는 상태에서 조회
        2. 200 OK 응답 확인
        3. 빈 배열 반환 확인
        """
        # Given: test_closet_items fixture 사용하지 않음 (빈 옷장)
        
        # When: top 카테고리 조회
        response = client.get("/api/v1/closet/top", headers=auth_headers)
        
        # Then: 빈 배열 반환
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_closet_items_invalid_category(self, client: TestClient, auth_headers: dict, 
                                               test_user: User):
        """
        잘못된 카테고리 조회 테스트
        
        시나리오:
        1. 존재하지 않는 카테고리로 조회
        2. 400 Bad Request 응답 확인
        3. 에러 메시지 확인
        """
        # Given: 잘못된 카테고리 "잘못된카테고리"
        
        # When: 잘못된 카테고리로 조회
        response = client.get("/api/v1/closet/잘못된카테고리", headers=auth_headers)
        
        # Then: 400 에러 응답
        assert response.status_code == 400
        
        data = response.json()["detail"]  # FastAPI의 HTTPException은 detail 필드에 정보를 담음
        assert data["status"] == "error"
        assert data["code"] == 400
        assert data["error"] == "Bad Request"
        assert "잘못된 카테고리" in data["message"]
        assert "top" in data["message"]
        assert "bottom" in data["message"]
        assert "shoes" in data["message"]
        assert "outer" in data["message"]
        assert data["detail"]["category"] == "잘못된카테고리"
    
    def test_get_closet_items_unauthorized(self, client: TestClient, test_user: User):
        """
        인증 없이 조회 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 요청
        2. 401 Unauthorized 응답 확인
        """
        # Given: 인증 헤더 없음
        
        # When: 인증 없이 조회
        response = client.get("/api/v1/closet/top")
        
        # Then: 401 에러 응답
        assert response.status_code == 401
        
        data = response.json()["detail"]  # FastAPI의 HTTPException은 detail 필드에 정보를 담음
        assert data["status"] == "error"
        assert data["code"] == 401
        assert data["error"] == "Unauthorized"
    
    def test_get_closet_items_all_categories(self, client: TestClient, auth_headers: dict,
                                             test_user: User, test_closet_items: list[ClosetItem]):
        """
        모든 카테고리 조회 테스트
        
        시나리오:
        1. top, bottom, shoes, outer 각각 조회
        2. 각 카테고리별 2개씩 반환 확인
        """
        # Given: 각 카테고리별 2개씩 아이템 존재
        categories = ["top", "bottom", "shoes", "outer"]
        
        for category in categories:
            # When: 각 카테고리 조회
            response = client.get(f"/api/v1/closet/{category}", headers=auth_headers)
            
            # Then: 각각 2개씩 반환
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2, f"{category} 카테고리에 2개가 있어야 함"


class TestCreateClosetItem:
    """옷장 아이템 추가 테스트"""
    
    def test_create_closet_item_success(self, client: TestClient, auth_headers: dict,
                                       test_user: User, test_db: Session):
        """
        옷 추가 성공 테스트
        
        시나리오:
        1. 새로운 top 추가
        2. 200 OK 응답 확인
        3. DB에 실제로 추가되었는지 확인
        """
        # Given: 추가할 아이템 데이터
        item_data = {"name": "gray hoodie"}
        
        # When: top 추가 요청
        response = client.post("/api/v1/closet/top", 
                              json=item_data, 
                              headers=auth_headers)
        
        # Then: 성공 응답 확인
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "추가 완료"
        
        # DB에 실제로 추가되었는지 확인
        item = test_db.query(ClosetItem).filter(
            ClosetItem.user_id == test_user.id,
            ClosetItem.category == "top",
            ClosetItem.name == "gray hoodie"
        ).first()
        
        assert item is not None
        assert item.name == "gray hoodie"
        assert item.category == "top"
        assert item.user_id == test_user.id
    
    def test_create_closet_item_invalid_category(self, client: TestClient, auth_headers: dict,
                                                 test_user: User):
        """
        잘못된 카테고리로 추가 시도 테스트
        
        시나리오:
        1. 존재하지 않는 카테고리로 추가 시도
        2. 400 Bad Request 응답 확인
        """
        # Given: 추가할 아이템 데이터
        item_data = {"name": "테스트 아이템"}
        
        # When: 잘못된 카테고리로 추가
        response = client.post("/api/v1/closet/잘못된카테고리",
                              json=item_data,
                              headers=auth_headers)
        
        # Then: 400 에러 응답
        assert response.status_code == 400
        
        data = response.json()["detail"]  # FastAPI의 HTTPException은 detail 필드에 정보를 담음
        assert data["status"] == "error"
        assert data["code"] == 400
        assert "잘못된 카테고리" in data["message"]
    
    def test_create_closet_item_missing_name(self, client: TestClient, auth_headers: dict,
                                            test_user: User):
        """
        이름 없이 추가 시도 테스트
        
        시나리오:
        1. name 필드 없이 요청
        2. 422 Unprocessable Entity 응답 확인 (FastAPI 자동 검증)
        """
        # Given: name 필드 없는 데이터
        item_data = {}
        
        # When: name 없이 추가 요청
        response = client.post("/api/v1/closet/top",
                              json=item_data,
                              headers=auth_headers)
        
        # Then: 422 에러 응답 (Pydantic 검증 실패)
        assert response.status_code == 422
    
    def test_create_closet_item_unauthorized(self, client: TestClient):
        """
        인증 없이 추가 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 요청
        2. 401 Unauthorized 응답 확인
        """
        # Given: 추가할 아이템 데이터
        item_data = {"name": "테스트 아이템"}
        
        # When: 인증 없이 추가
        response = client.post("/api/v1/closet/top", json=item_data)
        
        # Then: 401 에러 응답
        assert response.status_code == 401
    
    def test_create_closet_item_all_categories(self, client: TestClient, auth_headers: dict,
                                               test_user: User, test_db: Session):
        """
        모든 카테고리에 아이템 추가 테스트
        
        시나리오:
        1. top, bottom, shoes, outer 각각 추가
        2. 모두 성공하는지 확인
        """
        # Given: 각 카테고리별 아이템 데이터
        test_items = [
            ("top", "white shirt"),
            ("bottom", "jeans"),
            ("shoes", "loafers"),
            ("outer", "trench coat")
        ]
        
        for category, name in test_items:
            # When: 각 카테고리에 아이템 추가
            response = client.post(f"/api/v1/closet/{category}",
                                  json={"name": name},
                                  headers=auth_headers)
            
            # Then: 성공 응답
            assert response.status_code == 200
            assert response.json()["message"] == "추가 완료"
            
            # DB 확인
            item = test_db.query(ClosetItem).filter(
                ClosetItem.user_id == test_user.id,
                ClosetItem.category == category,
                ClosetItem.name == name
            ).first()
            assert item is not None


class TestDeleteClosetItem:
    """옷장 아이템 삭제 테스트"""
    
    def test_delete_closet_item_success(self, client: TestClient, auth_headers: dict,
                                       test_user: User, test_closet_items: list[ClosetItem],
                                       test_db: Session):
        """
        옷 삭제 성공 테스트
        
        시나리오:
        1. 기존 아이템 삭제
        2. 200 OK 응답 확인
        3. DB에서 실제로 삭제되었는지 확인
        """
        # Given: 삭제할 아이템 (첫 번째 아이템)
        item_to_delete = test_closet_items[0]
        item_id = item_to_delete.id
        
        # When: 아이템 삭제
        response = client.delete(f"/api/v1/closet/{item_id}", headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "삭제 완료"
        
        # DB에서 실제로 삭제되었는지 확인
        deleted_item = test_db.query(ClosetItem).filter(
            ClosetItem.id == item_id
        ).first()
        
        assert deleted_item is None
    
    def test_delete_closet_item_not_found(self, client: TestClient, auth_headers: dict,
                                         test_user: User):
        """
        존재하지 않는 아이템 삭제 시도 테스트
        
        시나리오:
        1. 존재하지 않는 ID로 삭제 시도
        2. 404 Not Found 응답 확인
        """
        # Given: 존재하지 않는 아이템 ID
        non_existent_id = 99999
        
        # When: 존재하지 않는 아이템 삭제 시도
        response = client.delete(f"/api/v1/closet/{non_existent_id}", 
                                headers=auth_headers)
        
        # Then: 404 에러 응답
        assert response.status_code == 404
        
        data = response.json()["detail"]  # FastAPI의 HTTPException은 detail 필드에 정보를 담음
        assert data["status"] == "error"
        assert data["code"] == 404
        assert data["error"] == "Not Found"
        assert "옷장 아이템을 찾을 수 없습니다" in data["message"]
        assert data["detail"]["resource"] == "closet_item"
        assert data["detail"]["id"] == non_existent_id
    
    def test_delete_closet_item_unauthorized(self, client: TestClient,
                                            test_closet_items: list[ClosetItem]):
        """
        인증 없이 삭제 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 삭제 시도
        2. 401 Unauthorized 응답 확인
        """
        # Given: 삭제할 아이템
        item_id = test_closet_items[0].id
        
        # When: 인증 없이 삭제 시도
        response = client.delete(f"/api/v1/closet/{item_id}")
        
        # Then: 401 에러 응답
        assert response.status_code == 401
    
    def test_delete_closet_item_multiple(self, client: TestClient, auth_headers: dict,
                                        test_user: User, test_closet_items: list[ClosetItem],
                                        test_db: Session):
        """
        여러 아이템 순차 삭제 테스트
        
        시나리오:
        1. 3개의 아이템을 순차적으로 삭제
        2. 각각 성공 확인
        3. DB에서 모두 삭제되었는지 확인
        """
        # Given: 삭제할 아이템 3개 선택
        items_to_delete = test_closet_items[:3]
        item_ids = [item.id for item in items_to_delete]
        
        # When & Then: 각 아이템 삭제
        for item_id in item_ids:
            response = client.delete(f"/api/v1/closet/{item_id}", 
                                    headers=auth_headers)
            
            assert response.status_code == 200
            assert response.json()["message"] == "삭제 완료"
        
        # DB에서 모두 삭제되었는지 확인
        for item_id in item_ids:
            deleted_item = test_db.query(ClosetItem).filter(
                ClosetItem.id == item_id
            ).first()
            assert deleted_item is None
        
        # 나머지 아이템은 여전히 존재하는지 확인
        remaining_items = test_db.query(ClosetItem).filter(
            ClosetItem.user_id == test_user.id
        ).all()
        assert len(remaining_items) == len(test_closet_items) - 3
    
    def test_delete_closet_item_twice(self, client: TestClient, auth_headers: dict,
                                     test_user: User, test_closet_items: list[ClosetItem]):
        """
        같은 아이템 두 번 삭제 시도 테스트
        
        시나리오:
        1. 아이템 삭제 성공
        2. 같은 아이템 다시 삭제 시도
        3. 404 Not Found 응답 확인
        """
        # Given: 삭제할 아이템
        item_id = test_closet_items[0].id
        
        # When: 첫 번째 삭제 (성공)
        response1 = client.delete(f"/api/v1/closet/{item_id}", headers=auth_headers)
        assert response1.status_code == 200
        
        # When: 두 번째 삭제 시도 (실패해야 함)
        response2 = client.delete(f"/api/v1/closet/{item_id}", headers=auth_headers)
        
        # Then: 404 에러 응답
        assert response2.status_code == 404
        data = response2.json()["detail"]  # FastAPI의 HTTPException은 detail 필드에 정보를 담음
        assert data["status"] == "error"
        assert data["code"] == 404

