"""
즐겨찾는 코디 라우터 테스트
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, ClosetItem, TodayOutfit, FavoriteOutfit


class TestGetFavorites:
    """즐겨찾는 코디 목록 조회 테스트"""
    
    def test_get_favorites_empty(self, client: TestClient, auth_headers: dict, test_user: User):
        """
        빈 즐겨찾기 목록 조회 테스트
        
        시나리오:
        1. 즐겨찾기가 없는 상태에서 조회
        2. 200 OK 응답 확인
        3. 빈 배열 반환 확인
        """
        # Given: 즐겨찾기 없음
        
        # When: 즐겨찾기 목록 조회
        response = client.get("/api/v1/favorites", headers=auth_headers)
        
        # Then: 빈 배열 반환
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_favorites_with_items(self, client: TestClient, auth_headers: dict,
                                     test_user: User, test_favorite_outfit: FavoriteOutfit):
        """
        즐겨찾기가 있는 상태에서 조회 테스트
        
        시나리오:
        1. 즐겨찾기 1개 존재
        2. 200 OK 응답 확인
        3. 목록에 id와 name이 올바르게 반환되는지 확인
        """
        # Given: test_favorite_outfit 존재
        
        # When: 즐겨찾기 목록 조회
        response = client.get("/api/v1/favorites", headers=auth_headers)
        
        # Then: 목록 반환
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_favorite_outfit.id
        assert data[0]["name"] == "주말 데일리룩"
    
    def test_get_favorites_multiple(self, client: TestClient, auth_headers: dict,
                                   test_user: User, test_today_outfit: TodayOutfit,
                                   test_closet_items: list[ClosetItem], test_db: Session):
        """
        여러 즐겨찾기 조회 테스트
        
        시나리오:
        1. 즐겨찾기 3개 생성
        2. 목록 조회
        3. 3개 모두 반환되는지 확인
        """
        # Given: 즐겨찾기 3개 생성 (각각 다른 조합)
        favorites_data = [
            {
                "name": "주말 코디",
                "상의_id": test_closet_items[0].id,
                "하의_id": test_closet_items[2].id,
                "신발_id": test_closet_items[4].id,
                "아우터_id": test_closet_items[6].id
            },
            {
                "name": "출근 코디",
                "상의_id": test_closet_items[1].id,  # 상의만 다름
                "하의_id": test_closet_items[2].id,
                "신발_id": test_closet_items[4].id,
                "아우터_id": test_closet_items[6].id
            },
            {
                "name": "데이트 코디",
                "상의_id": test_closet_items[0].id,
                "하의_id": test_closet_items[3].id,  # 하의만 다름
                "신발_id": test_closet_items[4].id,
                "아우터_id": test_closet_items[6].id
            }
        ]
        
        favorite_names = []
        for fav_data in favorites_data:
            favorite = FavoriteOutfit(
                user_id=test_user.id,
                name=fav_data["name"],
                상의_id=fav_data["상의_id"],
                하의_id=fav_data["하의_id"],
                신발_id=fav_data["신발_id"],
                아우터_id=fav_data["아우터_id"]
            )
            test_db.add(favorite)
            favorite_names.append(fav_data["name"])
        test_db.commit()
        
        # When: 목록 조회
        response = client.get("/api/v1/favorites", headers=auth_headers)
        
        # Then: 3개 반환
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        returned_names = [item["name"] for item in data]
        for name in favorite_names:
            assert name in returned_names
    
    def test_get_favorites_unauthorized(self, client: TestClient):
        """
        인증 없이 조회 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 요청
        2. 401 Unauthorized 응답 확인
        """
        # Given: 인증 헤더 없음
        
        # When: 인증 없이 조회
        response = client.get("/api/v1/favorites")
        
        # Then: 401 에러 응답
        assert response.status_code == 401


class TestGetFavorite:
    """특정 즐겨찾기 상세 조회 테스트"""
    
    def test_get_favorite_success(self, client: TestClient, auth_headers: dict,
                                  test_user: User, test_favorite_outfit: FavoriteOutfit,
                                  test_closet_items: list[ClosetItem]):
        """
        즐겨찾기 상세 조회 성공 테스트
        
        시나리오:
        1. 즐겨찾기 ID로 조회
        2. 200 OK 응답 확인
        3. 모든 아이템 정보가 올바르게 반환되는지 확인
        """
        # Given: test_favorite_outfit 존재
        
        # When: 즐겨찾기 상세 조회
        response = client.get(f"/api/v1/favorites/{test_favorite_outfit.id}",
                            headers=auth_headers)
        
        # Then: 상세 정보 반환
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "주말 데일리룩"
        assert data["상의"] is not None
        assert data["상의"]["name"] == "화이트 티셔츠"
        assert data["하의"] is not None
        assert data["하의"]["name"] == "베이지 팬츠"
        assert data["신발"] is not None
        assert data["신발"]["name"] == "화이트 운동화"
        assert data["아우터"] is not None
        assert data["아우터"]["name"] == "블루 데님 재킷"
    
    def test_get_favorite_not_found(self, client: TestClient, auth_headers: dict,
                                   test_user: User):
        """
        존재하지 않는 즐겨찾기 조회 테스트
        
        시나리오:
        1. 존재하지 않는 ID로 조회
        2. 404 Not Found 응답 확인
        """
        # Given: 존재하지 않는 ID
        non_existent_id = 99999
        
        # When: 존재하지 않는 즐겨찾기 조회
        response = client.get(f"/api/v1/favorites/{non_existent_id}",
                            headers=auth_headers)
        
        # Then: 404 에러 응답
        assert response.status_code == 404
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 404
        assert "즐겨찾는 코디를 찾을 수 없습니다" in data["message"]
    
    def test_get_favorite_unauthorized(self, client: TestClient,
                                      test_favorite_outfit: FavoriteOutfit):
        """
        인증 없이 조회 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 조회
        2. 401 Unauthorized 응답 확인
        """
        # Given: 인증 헤더 없음
        
        # When: 인증 없이 조회
        response = client.get(f"/api/v1/favorites/{test_favorite_outfit.id}")
        
        # Then: 401 에러 응답
        assert response.status_code == 401


class TestCreateFavorite:
    """즐겨찾기 생성 테스트"""
    
    def test_create_favorite_success(self, client: TestClient, auth_headers: dict,
                                    test_user: User, test_today_outfit: TodayOutfit,
                                    test_db: Session):
        """
        즐겨찾기 생성 성공 테스트
        
        시나리오:
        1. 완전한 오늘의 코디가 있는 상태
        2. 즐겨찾기로 저장
        3. 200 OK 응답 확인
        4. DB에 저장되었는지 확인
        5. 오늘의 코디가 초기화되었는지 확인
        """
        # Given: 완전한 오늘의 코디 존재 (test_today_outfit)
        
        # When: 즐겨찾기 저장
        response = client.post("/api/v1/favorites",
                              json={"name": "새로운 코디"},
                              headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        assert response.json()["message"] == "저장 완료"
        
        # DB에 저장되었는지 확인
        favorite = test_db.query(FavoriteOutfit).filter(
            FavoriteOutfit.user_id == test_user.id,
            FavoriteOutfit.name == "새로운 코디"
        ).first()
        assert favorite is not None
        assert favorite.상의_id is not None
        assert favorite.하의_id is not None
        assert favorite.신발_id is not None
        assert favorite.아우터_id is not None
        
        # 오늘의 코디가 초기화되었는지 확인
        test_db.expire_all()
        today_outfit = test_db.query(TodayOutfit).filter(
            TodayOutfit.user_id == test_user.id
        ).first()
        assert today_outfit.상의_id is None
        assert today_outfit.하의_id is None
        assert today_outfit.신발_id is None
        assert today_outfit.아우터_id is None
    
    def test_create_favorite_incomplete_outfit(self, client: TestClient, auth_headers: dict,
                                               test_user: User, empty_today_outfit: TodayOutfit):
        """
        불완전한 코디로 저장 시도 테스트
        
        시나리오:
        1. 일부 카테고리만 선택된 오늘의 코디
        2. 즐겨찾기로 저장 시도
        3. 400 Bad Request 응답 확인
        """
        # Given: 빈 오늘의 코디 (empty_today_outfit)
        
        # When: 불완전한 코디 저장 시도
        response = client.post("/api/v1/favorites",
                              json={"name": "불완전한 코디"},
                              headers=auth_headers)
        
        # Then: 400 에러 응답
        assert response.status_code == 400
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 400
        assert "코디를 완성해주세요" in data["message"]
    
    def test_create_favorite_duplicate_name(self, client: TestClient, auth_headers: dict,
                                           test_user: User, test_today_outfit: TodayOutfit,
                                           test_favorite_outfit: FavoriteOutfit):
        """
        중복된 이름으로 저장 시도 테스트
        
        시나리오:
        1. 이미 "주말 데일리룩"이라는 즐겨찾기 존재
        2. 같은 이름으로 저장 시도
        3. 409 Conflict 응답 확인
        """
        # Given: "주말 데일리룩" 즐겨찾기 이미 존재 (test_favorite_outfit)
        
        # When: 같은 이름으로 저장 시도
        response = client.post("/api/v1/favorites",
                              json={"name": "주말 데일리룩"},
                              headers=auth_headers)
        
        # Then: 409 에러 응답
        assert response.status_code == 409
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 409
        assert "이미 같은 이름의 즐겨찾는 코디가 있습니다" in data["message"]
    
    def test_create_favorite_duplicate_combination(self, client: TestClient, auth_headers: dict,
                                                   test_user: User, test_today_outfit: TodayOutfit,
                                                   test_favorite_outfit: FavoriteOutfit):
        """
        같은 조합의 코디로 저장 시도 테스트
        
        시나리오:
        1. 이미 저장된 즐겨찾기와 같은 조합의 오늘의 코디 존재
        2. 다른 이름으로 저장 시도
        3. 409 Conflict 응답 확인 및 기존 코디명 확인
        """
        # Given: test_favorite_outfit과 같은 조합의 test_today_outfit 존재
        # (test_favorite_outfit과 test_today_outfit은 같은 조합으로 설정됨)
        
        # When: 다른 이름으로 저장 시도
        response = client.post("/api/v1/favorites",
                              json={"name": "새로운 이름"},
                              headers=auth_headers)
        
        # Then: 409 에러 응답
        assert response.status_code == 409
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 409
        assert "이미 저장된 코디입니다" in data["message"]
        assert "주말 데일리룩" in data["message"]  # 기존 코디명 포함 확인
        assert data["detail"]["existing_name"] == "주말 데일리룩"
    
    def test_create_favorite_partial_outfit(self, client: TestClient, auth_headers: dict,
                                           test_user: User, empty_today_outfit: TodayOutfit,
                                           test_closet_items: list[ClosetItem], test_db: Session):
        """
        일부만 선택된 코디로 저장 시도 테스트
        
        시나리오:
        1. 상의, 하의만 선택된 코디
        2. 즐겨찾기로 저장 시도
        3. 400 Bad Request 응답 확인
        """
        # Given: 상의, 하의만 선택
        empty_today_outfit.상의_id = test_closet_items[0].id
        empty_today_outfit.하의_id = test_closet_items[2].id
        test_db.commit()
        
        # When: 불완전한 코디 저장 시도
        response = client.post("/api/v1/favorites",
                              json={"name": "불완전 코디"},
                              headers=auth_headers)
        
        # Then: 400 에러 응답
        assert response.status_code == 400
        
        data = response.json()["detail"]
        assert "코디를 완성해주세요" in data["message"]
    
    def test_create_favorite_unauthorized(self, client: TestClient):
        """
        인증 없이 저장 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 저장 시도
        2. 401 Unauthorized 응답 확인
        """
        # Given: 인증 헤더 없음
        
        # When: 인증 없이 저장 시도
        response = client.post("/api/v1/favorites", json={"name": "테스트"})
        
        # Then: 401 에러 응답
        assert response.status_code == 401


class TestUpdateFavorite:
    """즐겨찾기 이름 변경 테스트"""
    
    def test_update_favorite_name_success(self, client: TestClient, auth_headers: dict,
                                         test_user: User, test_favorite_outfit: FavoriteOutfit,
                                         test_db: Session):
        """
        즐겨찾기 이름 변경 성공 테스트
        
        시나리오:
        1. 기존 즐겨찾기 이름 변경
        2. 200 OK 응답 확인
        3. DB에 실제로 변경되었는지 확인
        """
        # Given: test_favorite_outfit 존재
        
        # When: 이름 변경 요청
        response = client.put(f"/api/v1/favorites/{test_favorite_outfit.id}",
                            json={"new_name": "변경된 코디"},
                            headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        assert "이름이 변경되었습니다" in response.json()["message"]
        
        # DB에서 확인
        test_db.expire_all()
        favorite = test_db.query(FavoriteOutfit).filter(
            FavoriteOutfit.id == test_favorite_outfit.id
        ).first()
        assert favorite.name == "변경된 코디"
    
    def test_update_favorite_name_not_found(self, client: TestClient, auth_headers: dict,
                                           test_user: User):
        """
        존재하지 않는 즐겨찾기 이름 변경 시도 테스트
        
        시나리오:
        1. 존재하지 않는 ID로 이름 변경 시도
        2. 404 Not Found 응답 확인
        """
        # Given: 존재하지 않는 ID
        non_existent_id = 99999
        
        # When: 존재하지 않는 즐겨찾기 이름 변경 시도
        response = client.put(f"/api/v1/favorites/{non_existent_id}",
                            json={"new_name": "새 이름"},
                            headers=auth_headers)
        
        # Then: 404 에러 응답
        assert response.status_code == 404
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 404
    
    def test_update_favorite_name_duplicate(self, client: TestClient, auth_headers: dict,
                                           test_user: User, test_favorite_outfit: FavoriteOutfit,
                                           test_closet_items: list[ClosetItem], test_db: Session):
        """
        중복된 이름으로 변경 시도 테스트
        
        시나리오:
        1. 즐겨찾기 2개 존재
        2. 하나를 다른 하나와 같은 이름으로 변경 시도
        3. 409 Conflict 응답 확인
        """
        # Given: 두 번째 즐겨찾기 생성
        favorite2 = FavoriteOutfit(
            user_id=test_user.id,
            name="출근 코디",
            상의_id=test_closet_items[0].id,
            하의_id=test_closet_items[2].id,
            신발_id=test_closet_items[4].id,
            아우터_id=test_closet_items[6].id
        )
        test_db.add(favorite2)
        test_db.commit()
        test_db.refresh(favorite2)
        
        # When: 첫 번째를 두 번째와 같은 이름으로 변경 시도
        response = client.put(f"/api/v1/favorites/{test_favorite_outfit.id}",
                            json={"new_name": "출근 코디"},
                            headers=auth_headers)
        
        # Then: 409 에러 응답
        assert response.status_code == 409
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 409
        assert "이미 같은 이름의 즐겨찾는 코디가 있습니다" in data["message"]
    
    def test_update_favorite_name_unauthorized(self, client: TestClient,
                                               test_favorite_outfit: FavoriteOutfit):
        """
        인증 없이 이름 변경 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 이름 변경 시도
        2. 401 Unauthorized 응답 확인
        """
        # Given: 인증 헤더 없음
        
        # When: 인증 없이 이름 변경 시도
        response = client.put(f"/api/v1/favorites/{test_favorite_outfit.id}",
                            json={"new_name": "새 이름"})
        
        # Then: 401 에러 응답
        assert response.status_code == 401


class TestDeleteFavorite:
    """즐겨찾기 삭제 테스트"""
    
    def test_delete_favorite_success(self, client: TestClient, auth_headers: dict,
                                    test_user: User, test_favorite_outfit: FavoriteOutfit,
                                    test_db: Session):
        """
        즐겨찾기 삭제 성공 테스트
        
        시나리오:
        1. 기존 즐겨찾기 삭제
        2. 200 OK 응답 확인
        3. DB에서 실제로 삭제되었는지 확인
        """
        # Given: test_favorite_outfit 존재
        favorite_id = test_favorite_outfit.id
        
        # When: 즐겨찾기 삭제
        response = client.delete(f"/api/v1/favorites/{favorite_id}",
                               headers=auth_headers)
        
        # Then: 성공 응답
        assert response.status_code == 200
        assert "삭제 완료" in response.json()["message"]
        
        # DB에서 삭제되었는지 확인
        deleted = test_db.query(FavoriteOutfit).filter(
            FavoriteOutfit.id == favorite_id
        ).first()
        assert deleted is None
    
    def test_delete_favorite_not_found(self, client: TestClient, auth_headers: dict,
                                      test_user: User):
        """
        존재하지 않는 즐겨찾기 삭제 시도 테스트
        
        시나리오:
        1. 존재하지 않는 ID로 삭제 시도
        2. 404 Not Found 응답 확인
        """
        # Given: 존재하지 않는 ID
        non_existent_id = 99999
        
        # When: 존재하지 않는 즐겨찾기 삭제 시도
        response = client.delete(f"/api/v1/favorites/{non_existent_id}",
                               headers=auth_headers)
        
        # Then: 404 에러 응답
        assert response.status_code == 404
        
        data = response.json()["detail"]
        assert data["status"] == "error"
        assert data["code"] == 404
        assert "즐겨찾는 코디를 찾을 수 없습니다" in data["message"]
    
    def test_delete_favorite_unauthorized(self, client: TestClient,
                                         test_favorite_outfit: FavoriteOutfit):
        """
        인증 없이 삭제 시도 테스트
        
        시나리오:
        1. Authorization 헤더 없이 삭제 시도
        2. 401 Unauthorized 응답 확인
        """
        # Given: 인증 헤더 없음
        
        # When: 인증 없이 삭제 시도
        response = client.delete(f"/api/v1/favorites/{test_favorite_outfit.id}")
        
        # Then: 401 에러 응답
        assert response.status_code == 401
    
    def test_delete_favorite_twice(self, client: TestClient, auth_headers: dict,
                                   test_user: User, test_favorite_outfit: FavoriteOutfit):
        """
        같은 즐겨찾기 두 번 삭제 시도 테스트
        
        시나리오:
        1. 즐겨찾기 삭제 성공
        2. 같은 즐겨찾기 다시 삭제 시도
        3. 404 Not Found 응답 확인
        """
        # Given: test_favorite_outfit 존재
        favorite_id = test_favorite_outfit.id
        
        # When: 첫 번째 삭제 (성공)
        response1 = client.delete(f"/api/v1/favorites/{favorite_id}",
                                 headers=auth_headers)
        assert response1.status_code == 200
        
        # When: 두 번째 삭제 시도 (실패해야 함)
        response2 = client.delete(f"/api/v1/favorites/{favorite_id}",
                                 headers=auth_headers)
        
        # Then: 404 에러 응답
        assert response2.status_code == 404
    
    def test_delete_multiple_favorites(self, client: TestClient, auth_headers: dict,
                                      test_user: User, test_closet_items: list[ClosetItem],
                                      test_db: Session):
        """
        여러 즐겨찾기 순차 삭제 테스트
        
        시나리오:
        1. 즐겨찾기 3개 생성
        2. 순차적으로 삭제
        3. 모두 성공하는지 확인
        """
        # Given: 즐겨찾기 3개 생성 (각각 다른 조합)
        favorites = []
        
        # 코디 1: 화이트 티셔츠, 베이지 팬츠, 화이트 운동화, 블루 데님 재킷
        favorite1 = FavoriteOutfit(
            user_id=test_user.id,
            name="코디 1",
            상의_id=test_closet_items[0].id,
            하의_id=test_closet_items[2].id,
            신발_id=test_closet_items[4].id,
            아우터_id=test_closet_items[6].id
        )
        test_db.add(favorite1)
        favorites.append(favorite1)
        
        # 코디 2: 블랙 후드티, 베이지 팬츠, 화이트 운동화, 블루 데님 재킷
        favorite2 = FavoriteOutfit(
            user_id=test_user.id,
            name="코디 2",
            상의_id=test_closet_items[1].id,  # 상의만 다름
            하의_id=test_closet_items[2].id,
            신발_id=test_closet_items[4].id,
            아우터_id=test_closet_items[6].id
        )
        test_db.add(favorite2)
        favorites.append(favorite2)
        
        # 코디 3: 화이트 티셔츠, 블랙 슬랙스, 화이트 운동화, 블루 데님 재킷
        favorite3 = FavoriteOutfit(
            user_id=test_user.id,
            name="코디 3",
            상의_id=test_closet_items[0].id,
            하의_id=test_closet_items[3].id,  # 하의만 다름
            신발_id=test_closet_items[4].id,
            아우터_id=test_closet_items[6].id
        )
        test_db.add(favorite3)
        favorites.append(favorite3)
        
        test_db.commit()
        for fav in favorites:
            test_db.refresh(fav)
        
        # When & Then: 각 즐겨찾기 삭제
        for favorite in favorites:
            response = client.delete(f"/api/v1/favorites/{favorite.id}",
                                   headers=auth_headers)
            assert response.status_code == 200
            assert "삭제 완료" in response.json()["message"]
        
        # 모두 삭제되었는지 확인
        remaining = test_db.query(FavoriteOutfit).filter(
            FavoriteOutfit.user_id == test_user.id
        ).all()
        assert len(remaining) == 0

