"""
인증 라우터
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas.user_schema import TokenResponse, UserResponse, UserSyncRequest, UserProfileUpdateRequest
from ..utils.auth_stub import TEST_TOKEN
from ..utils.dependencies import get_current_user, get_db
from ..models.user import User
from ..core.exceptions import BadRequestException
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/test-login", response_model=TokenResponse)
def test_login():
    """
    테스트용 토큰 발급 (개발/테스트용)
    
    Returns:
        TokenResponse: 테스트 토큰
    """
    return TokenResponse(token=TEST_TOKEN)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    현재 사용자 정보 조회
    
    Returns:
        UserResponse: 현재 사용자 정보 (id, firebase_uid, email, username, gender)
    """
    return UserResponse(
        id=current_user.id,
        firebase_uid=current_user.firebase_uid,
        email=current_user.email,
        username=current_user.username,
        gender=current_user.gender
    )


@router.post("/sync", response_model=UserResponse)
def sync_user_info(
    request: UserSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    사용자 정보 동기화 (회원가입 후 username, gender 업데이트)
    
    Args:
        request: 사용자 정보 동기화 요청 (username, gender)
        current_user: 현재 사용자 (Firebase 인증 필요)
        db: DB 세션
    
    Returns:
        UserResponse: 업데이트된 사용자 정보
    
    Raises:
        BadRequestException: 잘못된 입력값 (gender가 "남성" 또는 "여성"이 아닌 경우)
    """
    # gender 유효성 검증
    if request.gender not in ["남성", "여성"]:
        raise BadRequestException(
            message="성별은 '남성' 또는 '여성'만 입력 가능합니다.",
            detail={"gender": request.gender}
        )
    
    # username 유효성 검증 (빈 문자열 체크는 스키마에서 처리)
    if not request.username.strip():
        raise BadRequestException(
            message="사용자명은 공백만으로 구성될 수 없습니다.",
            detail={"username": request.username}
        )
    
    # 사용자 정보 업데이트
    try:
        current_user.username = request.username.strip()
        current_user.gender = request.gender
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"사용자 정보 동기화 완료: firebase_uid={current_user.firebase_uid}, username={current_user.username}")
        
        return UserResponse(
            id=current_user.id,
            firebase_uid=current_user.firebase_uid,
            email=current_user.email,
            username=current_user.username,
            gender=current_user.gender
        )
    except Exception as e:
        db.rollback()
        logger.error(f"사용자 정보 동기화 실패: {e}")
        raise BadRequestException(
            message="사용자 정보 업데이트 중 오류가 발생했습니다.",
            detail={"error": str(e)}
        )


@router.put("/sync", response_model=UserResponse)
def update_user_profile(
    request: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    사용자 프로필 수정 (username, gender 업데이트)
    
    Args:
        request: 프로필 수정 요청 (username, gender - 선택적)
        current_user: 현재 사용자 (Firebase 인증 필요)
        db: DB 세션
    
    Returns:
        UserResponse: 업데이트된 사용자 정보
    
    Raises:
        BadRequestException: 잘못된 입력값 (gender가 "남성" 또는 "여성"이 아닌 경우, 또는 업데이트할 필드가 없는 경우)
    """
    # 최소한 하나의 필드는 업데이트해야 함
    if request.username is None and request.gender is None:
        raise BadRequestException(
            message="최소한 하나의 필드(username 또는 gender)는 업데이트해야 합니다.",
            detail={}
        )
    
    # username 업데이트
    if request.username is not None:
        # username 유효성 검증
        if not request.username.strip():
            raise BadRequestException(
                message="사용자명은 공백만으로 구성될 수 없습니다.",
                detail={"username": request.username}
            )
        current_user.username = request.username.strip()
    
    # gender 업데이트
    if request.gender is not None:
        # gender 유효성 검증
        if request.gender not in ["남성", "여성"]:
            raise BadRequestException(
                message="성별은 '남성' 또는 '여성'만 입력 가능합니다.",
                detail={"gender": request.gender}
            )
        current_user.gender = request.gender
    
    # 사용자 정보 업데이트
    try:
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"사용자 프로필 수정 완료: firebase_uid={current_user.firebase_uid}, username={current_user.username}")
        
        return UserResponse(
            id=current_user.id,
            firebase_uid=current_user.firebase_uid,
            email=current_user.email,
            username=current_user.username,
            gender=current_user.gender
        )
    except Exception as e:
        db.rollback()
        logger.error(f"사용자 프로필 수정 실패: {e}")
        raise BadRequestException(
            message="사용자 정보 업데이트 중 오류가 발생했습니다.",
            detail={"error": str(e)}
        )

