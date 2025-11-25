"""
옷장 라우터 테스트
"""

import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, ClosetItem

# 테스트용 이미지 디렉터리 경로
TEST_IMAGES_DIR = Path(__file__).parent.parent / "fixtures" / "images"


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
        
        # 응답 구조 확인
        for item in data:
            assert "id" in item
            assert "feature" in item
            assert "image_url" in item
            assert isinstance(item["id"], int)
            assert isinstance(item["feature"], str)
            assert isinstance(item["image_url"], str)
    
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
        1. 새로운 top 추가 (이미지 파일 업로드)
        2. 200 OK 응답 확인
        3. DB에 실제로 추가되었는지 확인
        
        Note: Gemini API가 설정되어 있어야 합니다.
        """
        # Given: 테스트용 이미지 파일 생성
        from io import BytesIO
        from PIL import Image
        
        # 간단한 테스트 이미지 생성 (100x100 픽셀)
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # When: top 추가 요청
        response = client.post("/api/v1/closet/top",
                              files={"image": ("test.jpg", img_bytes, "image/jpeg")},
                              headers=auth_headers)
        
        # Then: 성공 응답 확인 (Gemini API가 없으면 400, 있으면 200)
        if response.status_code == 400:
            # Gemini API가 설정되지 않았거나 오류가 발생한 경우
            data = response.json()
            # API 키가 없거나 이미지 분석 실패 등의 경우
            pytest.skip(f"Gemini API가 설정되지 않았거나 오류가 발생했습니다: {data.get('message', 'Unknown error')}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "추가 완료"
        
        # DB에 실제로 추가되었는지 확인
        item = test_db.query(ClosetItem).filter(
            ClosetItem.user_id == test_user.id,
            ClosetItem.category == "top"
        ).order_by(ClosetItem.id.desc()).first()
        
        assert item is not None
        assert item.category == "top"
        assert item.user_id == test_user.id
        assert item.feature is not None
        assert item.image_url is not None
    
    def test_create_closet_item_invalid_category(self, client: TestClient, auth_headers: dict,
                                                 test_user: User):
        """
        잘못된 카테고리로 추가 시도 테스트
        
        시나리오:
        1. 존재하지 않는 카테고리로 추가 시도
        2. 400 Bad Request 응답 확인
        """
        # Given: 빈 파일 (실제로는 이미지 파일이 필요하지만 카테고리 검증만 테스트)
        from io import BytesIO
        
        # When: 잘못된 카테고리로 추가 시도
        response = client.post("/api/v1/closet/잘못된카테고리",
                              files={"image": ("test.jpg", BytesIO(b""), "image/jpeg")},
                              headers=auth_headers)
        
        # Then: 400 에러 응답 (FastAPI validation은 422이지만, 라우터에서 400 반환)
        assert response.status_code in [400, 422]
        
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
        # Given: 빈 파일 (인증 테스트만 수행)
        from io import BytesIO
        
        # When: 인증 없이 추가
        response = client.post("/api/v1/closet/top", 
                              files={"image": ("test.jpg", BytesIO(b""), "image/jpeg")})
        
        # Then: 401 에러 응답
        assert response.status_code == 401
    
    def test_create_closet_item_all_categories(self, client: TestClient, auth_headers: dict,
                                               test_user: User, test_db: Session):
        """
        모든 카테고리에 아이템 추가 테스트
        
        시나리오:
        1. top, bottom, shoes, outer 각각 추가 (이미지 파일 업로드)
        2. 모두 성공하는지 확인
        
        Note: Gemini API가 설정되어 있어야 합니다.
        """
        # Given: 테스트용 이미지 파일 생성
        from io import BytesIO
        from PIL import Image
        
        # 간단한 테스트 이미지 생성
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Given: 각 카테고리별 아이템 추가
        categories = ["top", "bottom", "shoes", "outer"]
        
        for category in categories:
            # 이미지 바이트를 다시 사용하기 위해 처음으로 이동
            img_bytes.seek(0)
            
            # When: 각 카테고리에 아이템 추가
            response = client.post(f"/api/v1/closet/{category}",
                                  files={"image": ("test.jpg", img_bytes, "image/jpeg")},
                                  headers=auth_headers)
            
            # Then: 성공 응답 확인 (Gemini API가 없으면 스킵)
            if response.status_code == 400:
                data = response.json()
                pytest.skip(f"Gemini API가 설정되지 않았거나 오류가 발생했습니다: {data.get('message', 'Unknown error')}")
            
            assert response.status_code == 200
            assert response.json()["message"] == "추가 완료"
            
            # DB 확인
            item = test_db.query(ClosetItem).filter(
                ClosetItem.user_id == test_user.id,
                ClosetItem.category == category
            ).order_by(ClosetItem.id.desc()).first()
            assert item is not None
            assert item.category == category
            assert item.feature is not None
            assert item.image_url is not None


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


class TestCreateClosetItemWithRealImage:
    """실제 이미지 파일을 사용한 옷장 아이템 추가 통합 테스트
    
    이 테스트는 실제 Gemini API를 호출하여 feature 추출이 제대로 동작하는지 확인합니다.
    tests/fixtures/images/ 디렉터리에 실제 옷 이미지 파일이 있어야 합니다.
    """
    
    def _get_test_image_path(self, category: str) -> Path:
        """테스트용 이미지 파일 경로 반환
        
        여러 파일명 패턴을 시도합니다:
        1. test_{category}.jpg
        2. tests_{category}.jpg
        3. {category}.jpg
        """
        # 카테고리별 이미지 파일명 패턴들
        patterns = [
            f"test_{category}.jpg",
            f"tests_{category}.jpg",
            f"{category}.jpg"
        ]
        
        # 각 패턴을 시도하여 존재하는 파일 반환
        for pattern in patterns:
            image_path = TEST_IMAGES_DIR / pattern
            if image_path.exists():
                return image_path
        
        # 기본값 반환 (존재하지 않을 수 있음)
        return TEST_IMAGES_DIR / patterns[0]
    
    def test_create_closet_item_with_real_image(self, client: TestClient, auth_headers: dict,
                                                test_user: User, test_db: Session):
        """
        실제 이미지 파일로 옷 추가 통합 테스트
        
        시나리오:
        1. tests/fixtures/images/tests_top.jpg 파일 사용
        2. 실제 Gemini API 호출하여 feature 추출
        3. 추출된 feature 형식 검증
        """
        # Given: 실제 이미지 파일 경로
        image_path = self._get_test_image_path("top")
        
        # 이미지 파일이 없으면 스킵
        if not image_path.exists():
            pytest.skip(f"테스트용 이미지 파일이 없습니다: {image_path}\n"
                       f"tests/fixtures/images/ 디렉터리에 tests_top.jpg 파일을 추가해주세요.")
        
        # When: 실제 이미지 파일로 top 추가 요청
        with open(image_path, "rb") as f:
            response = client.post("/api/v1/closet/top",
                                  files={"image": ("tests_top.jpg", f, "image/jpeg")},
                                  headers=auth_headers)
        
        # Then: 성공 응답 확인
        if response.status_code == 400:
            data = response.json()
            pytest.skip(f"Gemini API 오류: {data.get('message', 'Unknown error')}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "추가 완료"
        
        # DB에 실제로 추가되었는지 확인
        item = test_db.query(ClosetItem).filter(
            ClosetItem.user_id == test_user.id,
            ClosetItem.category == "top"
        ).order_by(ClosetItem.id.desc()).first()
        
        assert item is not None
        assert item.category == "top"
        assert item.user_id == test_user.id
        assert item.feature is not None
        assert item.image_url is not None
        
        # Feature 형식 검증 (카테고리_색상_재질_상세정보_성별_계절_스타일)
        feature_parts = item.feature.split("_")
        assert len(feature_parts) >= 7, f"Feature 형식이 올바르지 않습니다: {item.feature}"
        assert feature_parts[0] in ["상의", "하의", "신발", "아우터"], f"첫 번째 부분은 카테고리여야 합니다: {item.feature}"
        
        # Gemini API가 실제로 feature를 추출했는지 확인
        # (빈 문자열이 아니고, 최소한의 정보가 있어야 함)
        assert len(item.feature) > 10, f"Feature가 너무 짧습니다: {item.feature}"
    
    def test_create_closet_item_all_categories_with_real_images(self, client: TestClient, 
                                                                 auth_headers: dict,
                                                                 test_user: User, 
                                                                 test_db: Session):
        """
        모든 카테고리에 실제 이미지 파일로 추가 통합 테스트
        
        시나리오:
        1. 각 카테고리별 실제 이미지 파일 사용
        2. 실제 Gemini API 호출하여 feature 추출
        3. 모든 카테고리에서 성공하는지 확인
        
        Note:
        - tests/fixtures/images/ 디렉터리에 각 카테고리별 이미지 파일이 있어야 합니다
        - 파일이 없으면 해당 카테고리는 스킵
        """
        categories = ["top", "bottom", "shoes", "outer"]
        skipped_categories = []
        
        for category in categories:
            # Given: 실제 이미지 파일 경로
            image_path = self._get_test_image_path(category)
            
            # 이미지 파일이 없으면 스킵
            if not image_path.exists():
                skipped_categories.append(category)
                continue
            
            # When: 실제 이미지 파일로 추가 요청
            with open(image_path, "rb") as f:
                response = client.post(f"/api/v1/closet/{category}",
                                      files={"image": (image_path.name, f, "image/jpeg")},
                                      headers=auth_headers)
            
            # Then: 성공 응답 확인
            if response.status_code == 400:
                data = response.json()
                pytest.skip(f"Gemini API 오류 ({category}): {data.get('message', 'Unknown error')}")
            
            assert response.status_code == 200, f"{category} 카테고리 추가 실패"
            assert response.json()["message"] == "추가 완료"
            
            # DB 확인
            item = test_db.query(ClosetItem).filter(
                ClosetItem.user_id == test_user.id,
                ClosetItem.category == category
            ).order_by(ClosetItem.id.desc()).first()
            
            assert item is not None, f"{category} 아이템이 DB에 저장되지 않았습니다"
            assert item.category == category
            assert item.feature is not None, f"{category} feature가 None입니다"
            assert item.image_url is not None, f"{category} image_url이 None입니다"
            
            # Feature 형식 검증
            feature_parts = item.feature.split("_")
            assert len(feature_parts) >= 7, f"{category} Feature 형식이 올바르지 않습니다: {item.feature}"
            assert feature_parts[0] in ["상의", "하의", "신발", "아우터"], \
                f"{category} 첫 번째 부분은 카테고리여야 합니다: {item.feature}"
        
        # 스킵된 카테고리 정보 출력
        if skipped_categories:
            print(f"\n⚠️ 다음 카테고리의 이미지 파일이 없어 스킵되었습니다: {', '.join(skipped_categories)}")
            print(f"   tests/fixtures/images/ 디렉터리에 이미지 파일을 추가하면 테스트가 실행됩니다.")

