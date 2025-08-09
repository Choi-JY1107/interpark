import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import base64
import logging
from typing import Optional
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class CaptchaSolver:
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
    def solve(self, captcha_element: WebElement) -> Optional[str]:
        """캡차 이미지를 해결하고 텍스트 반환"""
        try:
            image = self._capture_element_image(captcha_element)
            processed_image = self._preprocess_image(image)
            text = self._perform_ocr(processed_image)
            cleaned_text = self._clean_text(text)
            
            logger.info(f"Captcha solved: {cleaned_text}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to solve captcha: {str(e)}")
            return None
            
    def _capture_element_image(self, element: WebElement) -> np.ndarray:
        """웹 요소를 이미지로 캡처"""
        captcha_base64 = element.screenshot_as_base64
        image_data = base64.b64decode(captcha_base64)
        image = Image.open(io.BytesIO(image_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """이미지 전처리"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        denoised = cv2.medianBlur(gray, 3)
        
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return morph
        
    def _perform_ocr(self, image: np.ndarray) -> str:
        """OCR 수행"""
        try:
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            return ""
            
    def _clean_text(self, text: str) -> str:
        """텍스트 정제"""
        cleaned = ''.join(c for c in text if c.isalnum())
        cleaned = cleaned.upper()
        
        common_mistakes = {
            'O': '0', 'I': '1', 'Z': '2',
            'S': '5', 'G': '6', 'B': '8'
        }
        
        if len(cleaned) == 4:
            for old, new in common_mistakes.items():
                if old in cleaned:
                    cleaned = cleaned.replace(old, new, 1)
                    
        return cleaned