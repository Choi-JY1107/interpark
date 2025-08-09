from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class WebDriverManager:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        
    def initialize(self, headless: bool = False, wait_timeout: int = 10):
        """웹드라이버 초기화"""
        try:
            options = webdriver.ChromeOptions()
            
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if headless:
                options.add_argument('--headless')
                
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # ChromeDriver 자동 설치 및 실행
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            self.wait = WebDriverWait(self.driver, wait_timeout)
            
            logger.info("WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
            
    def get_driver(self) -> webdriver.Chrome:
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        return self.driver
        
    def get_wait(self) -> WebDriverWait:
        if not self.wait:
            raise RuntimeError("WebDriverWait not initialized")
        return self.wait
        
    def quit(self):
        """웹드라이버 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None
                self.wait = None