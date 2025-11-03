from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class ClosetMateException(HTTPException):
    """공통 예외 처리 베이스 클래스"""
    
    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "status": "error",
                "code": status_code,
                "error": error,
                "message": message,
                "detail": detail or {}
            }
        )


class BadRequestException(ClosetMateException):
    """400 Bad Request"""
    
    def __init__(self, message: str = "잘못된 요청입니다. 입력값을 확인하세요.", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="Bad Request",
            message=message,
            detail=detail
        )


class UnauthorizedException(ClosetMateException):
    """401 Unauthorized"""
    
    def __init__(self, message: str = "유효하지 않은 인증 토큰입니다.", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="Unauthorized",
            message=message,
            detail=detail
        )


class NotFoundException(ClosetMateException):
    """404 Not Found"""
    
    def __init__(self, message: str = "요청하신 리소스를 찾을 수 없습니다.", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="Not Found",
            message=message,
            detail=detail
        )


class ConflictException(ClosetMateException):
    """409 Conflict"""
    
    def __init__(self, message: str = "이미 존재하는 리소스입니다.", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error="Conflict",
            message=message,
            detail=detail
        )


class InternalServerErrorException(ClosetMateException):
    """500 Internal Server Error"""
    
    def __init__(self, message: str = "서버 내부 오류가 발생했습니다.", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
            detail=detail
        )

