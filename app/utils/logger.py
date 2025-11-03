import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "closetmate",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    로거 설정 함수
    
    Args:
        name: 로거 이름
        level: 로깅 레벨 (기본: INFO)
        format_string: 커스텀 포맷 문자열
    
    Returns:
        logging.Logger: 설정된 로거
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 핸들러가 이미 있으면 중복 생성 방지
    if logger.handlers:
        return logger
    
    # 콘솔 핸들러 생성
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 포맷터 생성
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(console_handler)
    
    return logger


# 기본 로거 인스턴스 생성
logger = setup_logger()

