import os
from typing import Dict, Any


class Settings:
    """애플리케이션 설정"""
    
    # WebDriver 설정
    WEBDRIVER_TIMEOUT = 10
    WEBDRIVER_HEADLESS = False
    
    # 재시도 설정
    MAX_QUEUE_RETRY = 60
    MAX_SEAT_RETRY = 100
    
    # 로그 설정
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # OCR 설정
    TESSERACT_CONFIG = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """모든 설정 반환"""
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not callable(getattr(cls, attr)) and not attr.startswith("_")
        }