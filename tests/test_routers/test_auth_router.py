"""
인증 라우터 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthRouter:
    """인증 API 테스트"""
    
    def test_test_login_success(self, client: TestClient):
        """
        테스트 토큰 발급 성공 테스트
        
        시나리오:
        1. GET /api/v1/auth/test-login 요청
        2. 200 OK 응답 확인
        3. token 필드에 "test-token" 값 확인
        """
        # Given: 인증 없이 요청
        
        # When: 테스트 로그인 엔드포인트 호출
        response = client.get("/api/v1/auth/test-login")
        
        # Then: 성공 응답 확인
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert data["token"] == "test-token"
    
    def test_test_login_response_structure(self, client: TestClient):
        """
        테스트 토큰 응답 구조 검증
        
        시나리오:
        1. 응답이 올바른 JSON 구조인지 확인
        2. 필수 필드가 모두 포함되어 있는지 확인
        """
        # When
        response = client.get("/api/v1/auth/test-login")
        
        # Then
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 1  # token 필드만 존재
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0  # 빈 문자열이 아님

