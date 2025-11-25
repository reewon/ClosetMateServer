"""
Gemini API 서비스
- 이미지에서 옷의 피쳐 정보 추출 (category_detail, 계절, 색상, 재질, 스타일)
"""

import os
import re
from typing import Optional
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from ..core.config import settings
from ..core.exceptions import BadRequestException


# Gemini API 프롬프트
GEMINI_PROMPT = """
이 옷에 대해 category_detail, 계절, 색상, 재질, 스타일을 반드시 대답해줘.

category_detail은 다음 중 하나로: 
상의(맨투맨/스웨트, 후드 티셔츠, 셔츠/블라우스, 긴소매 티셔츠, 반소매 티셔츠, 피케/카라 티셔츠, 니트/스웨터, 민소매 티셔츠, 기타 상의), 
아우터(후드 집업, 블루종/MA-1, 레더/라이더스 재킷, 카디건, 트리커 재킷, 슈트/블레이저 재킷, 스타디움 재킷, 나일론/코치 재킷, 아노락 재킷, 트레이닝 재킷, 환절기 코트, 
사파리/헌팅 재킷, 베스트, 숏패딩/헤비 아우터, 무스탕/퍼, 폴리스/뽀글이, 겨울 싱글 코트, 겨울 더블 코트, 겨울 기타 코트, 롱패딩/헤비 아우터, 패딩 베스트, 기타 아우터), 
하의(데님 팬츠, 트레이닝/조거 팬츠, 코튼 팬츠, 슈트 팬츠/슬랙스, 숏 팬츠, 레깅스, 점프 슈트/오버올, 기타 하의), 
신발(스니커즈, 패딩/퍼 신발, 부츠/워크, 구두, 샌들/슬리퍼, 스포츠화, 신발용품) 중 하나를 선택.

색상은 white, black, gray, navy, blue, brown, beige, green, yellow, orange, red, pink, purple 중 하나.

재질은 cotton, polyester, silk, wool, leather, denim 중 하나.

계절은 봄, 여름, 가을, 겨울 중 하나.

스타일은 casual, minimal, street, sporty 중 하나.

반드시 아래 형식으로 대답해:

'category_detail: [값], 계절: [값], 색상: [값], 재질: [값], 스타일: [값]'

예시: 'category_detail: 숏 팬츠, 계절: 여름, 색상: gray, 재질: cotton, 스타일: casual'
"""


def _initialize_gemini() -> None:
    """
    Gemini API 초기화
    
    Raises:
        BadRequestException: API 키가 설정되지 않은 경우
    """
    if not settings.GEMINI_API_KEY:
        raise BadRequestException(
            message="Gemini API 키가 설정되지 않았습니다.",
            detail={"config": "GEMINI_API_KEY"}
        )
    
    genai.configure(api_key=settings.GEMINI_API_KEY)


def _parse_gemini_response(response_text: str) -> dict:
    """
    Gemini API 응답 텍스트를 파싱하여 딕셔너리로 변환
    
    Args:
        response_text: Gemini API 응답 텍스트
    
    Returns:
        dict: 파싱된 피쳐 정보 (성별 제외)
        예: {
            "category_detail": "숏 팬츠",
            "season": "여름",
            "color": "gray",
            "material": "cotton",
            "style": "casual"
        }
    
    Raises:
        BadRequestException: 파싱 실패 시
    """
    # 정규표현식으로 각 필드 추출 (성별 제외)
    patterns = {
        "category_detail": r"category_detail:\s*([^,]+)",
        "season": r"계절:\s*([^,]+)",
        "color": r"색상:\s*([^,]+)",
        "material": r"재질:\s*([^,]+)",
        "style": r"스타일:\s*([^,]+)"
    }
    
    result = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            result[key] = match.group(1).strip()
        else:
            raise BadRequestException(
                message=f"Gemini API 응답에서 {key}를 찾을 수 없습니다.",
                detail={"response": response_text}
            )
    
    return result


def _format_feature_string(parsed_data: dict, category: str, user_gender: str) -> str:
    """
    파싱된 데이터를 feature 문자열 형식으로 변환
    
    Args:
        parsed_data: 파싱된 피쳐 정보 (성별 제외)
        category: 카테고리 (top, bottom, shoes, outer)
        user_gender: 사용자 성별 (남성, 여성)
    
    Returns:
        str: 포맷된 feature 문자열
        예: '하의_gray_cotton_숏 팬츠_남성_여름_casual'
    """
    # 카테고리 한글 변환
    category_map = {
        "top": "상의",
        "bottom": "하의",
        "shoes": "신발",
        "outer": "아우터"
    }
    category_kr = category_map.get(category, category)
    
    # feature 형식: [카테고리]_[색상]_[재질]_[category_detail]_[성별]_[계절]_[스타일]
    # 성별은 사용자 정보에서 가져옴
    feature = f"{category_kr}_{parsed_data['color']}_{parsed_data['material']}_{parsed_data['category_detail']}_{user_gender}_{parsed_data['season']}_{parsed_data['style']}"
    
    return feature


def analyze_clothing_image(image_path: str, category: str, user_gender: str = "남성") -> str:
    """
    이미지에서 옷의 피쳐 정보를 추출하는 함수
    (이미지가 서버 파일 시스템에 저장되어 있는 경우; 저장된 이미지 재분석 시)
    
    Args:
        image_path: 이미지 파일 경로
        category: 카테고리 (top, bottom, shoes, outer)
        user_gender: 사용자 성별 (남성, 여성) - 기본값: "남성"
    
    Returns:
        str: 추출된 feature 문자열
        예: '하의_gray_cotton_숏 팬츠_남성_여름_casual'
    
    Raises:
        BadRequestException: 이미지 파일이 없거나, API 호출 실패 시
    """
    # Gemini API 초기화
    _initialize_gemini()
    
    # 이미지 파일 존재 확인
    if not os.path.exists(image_path):
        raise BadRequestException(
            message="이미지 파일을 찾을 수 없습니다.",
            detail={"image_path": image_path}
        )
    
    try:
        # 이미지 로드
        image = Image.open(image_path)
        
        # Gemini 모델 선택
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # 이미지와 프롬프트를 함께 전달하여 분석
        response = model.generate_content([GEMINI_PROMPT, image])
        
        # 응답 텍스트 추출 및 검증
        if not hasattr(response, 'text') or response.text is None:
            raise BadRequestException(
                message="Gemini API가 응답을 반환하지 않았습니다.",
                detail={"error": "response.text is None", "image_path": image_path}
            )
        
        response_text = response.text.strip()
        
        if not response_text:
            raise BadRequestException(
                message="Gemini API 응답이 비어있습니다.",
                detail={"error": "response.text is empty", "image_path": image_path}
            )
        
        # 응답 파싱
        parsed_data = _parse_gemini_response(response_text)
        
        # feature 문자열 형식으로 변환 (사용자 성별 사용)
        feature = _format_feature_string(parsed_data, category, user_gender)
        
        # 최종 feature 검증
        if not feature or not feature.strip():
            raise BadRequestException(
                message="Feature 정보를 추출할 수 없습니다.",
                detail={"error": "feature is empty", "parsed_data": parsed_data, "image_path": image_path}
            )
        
        return feature
        
    except BadRequestException:
        # BadRequestException은 그대로 전달
        raise
    except Exception as e:
        # Gemini API 오류 처리
        error_message = str(e)
        if "API key" in error_message or "authentication" in error_message.lower():
            raise BadRequestException(
                message="Gemini API 인증에 실패했습니다. API 키를 확인해주세요.",
                detail={"error": error_message, "image_path": image_path}
            )
        elif "quota" in error_message.lower() or "limit" in error_message.lower():
            raise BadRequestException(
                message="Gemini API 사용량 한도를 초과했습니다.",
                detail={"error": error_message, "image_path": image_path}
            )
        else:
            raise BadRequestException(
                message=f"이미지 분석 중 오류가 발생했습니다: {error_message}",
                detail={"error": error_message, "image_path": image_path}
            )


def analyze_clothing_image_from_bytes(image_bytes: bytes, category: str, user_gender: str = "남성") -> str:
    """
    바이너리 이미지 데이터에서 옷의 피쳐 정보를 추출하는 함수
    (FastAPI의 UploadFile에서 받은 이미지 데이터를 바로 처리)
    
    Args:
        image_bytes: 이미지 바이너리 데이터
        category: 카테고리 (top, bottom, shoes, outer)
        user_gender: 사용자 성별 (남성, 여성) - 기본값: "남성"
    
    Returns:
        str: 추출된 feature 문자열
        예: '하의_gray_cotton_숏 팬츠_남성_여름_casual'
    
    Raises:
        BadRequestException: 이미지 처리 실패 또는 API 호출 실패 시
    """
    # Gemini API 초기화
    _initialize_gemini()
    
    try:
        # 바이너리 데이터를 PIL Image로 변환
        from io import BytesIO
        image = Image.open(BytesIO(image_bytes))
        
        # Gemini 모델 선택
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # 이미지와 프롬프트를 함께 전달하여 분석
        response = model.generate_content([GEMINI_PROMPT, image])
        
        # 응답 텍스트 추출 및 검증
        if not hasattr(response, 'text') or response.text is None:
            raise BadRequestException(
                message="Gemini API가 응답을 반환하지 않았습니다.",
                detail={"error": "response.text is None"}
            )
        
        response_text = response.text.strip()
        
        if not response_text:
            raise BadRequestException(
                message="Gemini API 응답이 비어있습니다.",
                detail={"error": "response.text is empty"}
            )
        
        # 응답 파싱
        parsed_data = _parse_gemini_response(response_text)
        
        # feature 문자열 형식으로 변환 (사용자 성별 사용)
        feature = _format_feature_string(parsed_data, category, user_gender)
        
        # 최종 feature 검증
        if not feature or not feature.strip():
            raise BadRequestException(
                message="Feature 정보를 추출할 수 없습니다.",
                detail={"error": "feature is empty", "parsed_data": parsed_data}
            )
        
        return feature
        
    except BadRequestException:
        # BadRequestException은 그대로 전달
        raise
    except Exception as e:
        # Gemini API 오류 처리
        error_message = str(e)
        if "API key" in error_message or "authentication" in error_message.lower():
            raise BadRequestException(
                message="Gemini API 인증에 실패했습니다. API 키를 확인해주세요.",
                detail={"error": error_message}
            )
        elif "quota" in error_message.lower() or "limit" in error_message.lower():
            raise BadRequestException(
                message="Gemini API 사용량 한도를 초과했습니다.",
                detail={"error": error_message}
            )
        else:
            raise BadRequestException(
                message=f"이미지 분석 중 오류가 발생했습니다: {error_message}",
                detail={"error": error_message}
            )

