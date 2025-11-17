"""
파일 저장 서비스
- 추상화 설계로 로컬 파일 시스템과 클라우드 스토리지(S3 등) 전환 가능
- 현재는 LocalFileStorage 구현
"""

import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO
from ..core.config import settings
from ..core.exceptions import BadRequestException, InternalServerErrorException


class StorageService(ABC):
    """파일 저장 서비스 추상 클래스"""
    
    @abstractmethod
    def save_image(self, image_bytes: bytes, user_id: int, item_id: int, file_extension: str) -> str:
        """
        이미지를 저장하고 URL을 반환
        
        Args:
            image_bytes: 이미지 바이너리 데이터
            user_id: 사용자 ID
            item_id: 아이템 ID
            file_extension: 파일 확장자 (예: "jpg", "png")
        
        Returns:
            str: 저장된 이미지의 URL 또는 경로
        """
        pass
    
    @abstractmethod
    def delete_image(self, image_url: str) -> bool:
        """
        이미지 삭제
        
        Args:
            image_url: 삭제할 이미지의 URL 또는 경로
        
        Returns:
            bool: 삭제 성공 여부
        """
        pass
    
    @abstractmethod
    def get_image_path(self, image_url: str) -> str:
        """
        이미지 URL을 실제 파일 경로로 변환
        
        Args:
            image_url: 이미지 URL 또는 경로
        
        Returns:
            str: 실제 파일 경로
        """
        pass


class LocalFileStorage(StorageService):
    """로컬 파일 시스템 저장 구현"""
    
    def __init__(self, base_dir: str = None):
        """
        LocalFileStorage 초기화
        
        Args:
            base_dir: 기본 업로드 디렉토리 (기본값: settings.UPLOAD_DIR)
        """
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)
        self._ensure_base_dir()
    
    def _ensure_base_dir(self) -> None:
        """기본 디렉토리 생성"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_user_dir(self, user_id: int) -> Path:
        """
        사용자별 디렉토리 경로 반환
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            Path: 사용자 디렉토리 경로
        """
        user_dir = self.base_dir / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def _validate_file_extension(self, file_extension: str) -> None:
        """
        파일 확장자 검증
        
        Args:
            file_extension: 파일 확장자
        
        Raises:
            BadRequestException: 허용되지 않은 확장자인 경우
        """
        allowed_extensions = {"jpg", "jpeg", "png", "gif", "webp"}
        if file_extension.lower() not in allowed_extensions:
            raise BadRequestException(
                message=f"허용되지 않은 파일 형식입니다. 가능한 형식: {', '.join(allowed_extensions)}",
                detail={"file_extension": file_extension}
            )
    
    def save_image(self, image_bytes: bytes, user_id: int, item_id: int, file_extension: str) -> str:
        """
        이미지를 저장하고 상대 경로를 반환
        
        Args:
            image_bytes: 이미지 바이너리 데이터
            user_id: 사용자 ID
            item_id: 아이템 ID
            file_extension: 파일 확장자 (예: "jpg", "png")
        
        Returns:
            str: 저장된 이미지의 상대 경로 (예: "uploads/user_1/item_123.jpg")
        
        Raises:
            BadRequestException: 파일 확장자가 허용되지 않은 경우
            InternalServerErrorException: 파일 저장 실패 시
        """
        # 파일 확장자 검증
        self._validate_file_extension(file_extension)
        
        # 사용자 디렉토리 가져오기
        user_dir = self._get_user_dir(user_id)
        
        # 파일명 생성 (item_id와 UUID를 조합하여 고유성 보장)
        # 형식: item_{item_id}_{uuid}.{extension}
        unique_id = str(uuid.uuid4())[:8]  # UUID 앞 8자리만 사용
        filename = f"item_{item_id}_{unique_id}.{file_extension.lower()}"
        file_path = user_dir / filename
        
        try:
            # 파일 저장
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            
            # 상대 경로 반환 (OS 독립적인 경로 구분자 사용)
            relative_path = str(file_path).replace("\\", "/")
            return relative_path
            
        except Exception as e:
            raise InternalServerErrorException(
                message=f"이미지 저장 중 오류가 발생했습니다: {str(e)}",
                detail={"user_id": user_id, "item_id": item_id, "error": str(e)}
            )
    
    def delete_image(self, image_url: str) -> bool:
        """
        이미지 삭제
        
        Args:
            image_url: 삭제할 이미지의 경로
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            file_path = Path(image_url)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            # 삭제 실패는 로그만 남기고 예외를 발생시키지 않음
            # (이미 삭제된 파일일 수 있음)
            print(f"이미지 삭제 실패: {image_url}, 오류: {str(e)}")
            return False
    
    def get_image_path(self, image_url: str) -> str:
        """
        이미지 URL을 실제 파일 경로로 변환(추후 S3와 같은 클라우드 스토리지로 변경 시 사용)
        
        Args:
            image_url: 이미지 URL 또는 경로
        
        Returns:
            str: 실제 파일 경로
        """
        # 로컬 파일 시스템의 경우 URL과 경로가 동일
        return image_url


# 기본 StorageService 인스턴스 (싱글톤 패턴)
_default_storage: StorageService = None


def get_storage_service() -> StorageService:
    """
    기본 StorageService 인스턴스 반환
    
    Returns:
        StorageService: 기본 저장 서비스 인스턴스
    """
    global _default_storage
    if _default_storage is None:
        _default_storage = LocalFileStorage()
    return _default_storage


def save_image(image_bytes: bytes, user_id: int, item_id: int, file_extension: str) -> str:
    """
    이미지를 저장하는 편의 함수
    
    Args:
        image_bytes: 이미지 바이너리 데이터
        user_id: 사용자 ID
        item_id: 아이템 ID
        file_extension: 파일 확장자
    
    Returns:
        str: 저장된 이미지의 경로
    """
    storage = get_storage_service()
    return storage.save_image(image_bytes, user_id, item_id, file_extension)


def delete_image(image_url: str) -> bool:
    """
    이미지를 삭제하는 편의 함수
    
    Args:
        image_url: 삭제할 이미지의 경로
    
    Returns:
        bool: 삭제 성공 여부
    """
    storage = get_storage_service()
    return storage.delete_image(image_url)

