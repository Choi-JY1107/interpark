from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
from typing import Optional

from domain.entities import Reservation
from domain.repositories.reservation_repository import ReservationRepository
from infrastructure.web_driver.driver_manager import WebDriverManager
from infrastructure.ocr.captcha_solver import CaptchaSolver
from infrastructure.interpark.seat_selector import SeatSelector

logger = logging.getLogger(__name__)


class InterparkRepository(ReservationRepository):
    def __init__(self, driver_manager: WebDriverManager):
        self.driver_manager = driver_manager
        self.captcha_solver = CaptchaSolver()
        self.seat_selector: Optional[SeatSelector] = None
        
    def enter_queue(self, reservation: Reservation) -> bool:
        """대기열 진입"""
        try:
            driver = self.driver_manager.get_driver()
            wait = self.driver_manager.get_wait()
            
            driver.get(reservation.performance.url)
            
            retry_count = 0
            max_retries = 60
            
            while retry_count < max_retries:
                try:
                    book_button = wait.until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "btn_book"))
                    )
                    book_button.click()
                    logger.info("Successfully entered queue")
                    return True
                    
                except TimeoutException:
                    retry_count += 1
                    logger.debug(f"Retrying queue entry... ({retry_count}/{max_retries})")
                    time.sleep(0.5)
                    driver.refresh()
                    
            logger.error("Failed to enter queue after maximum retries")
            return False
            
        except Exception as e:
            logger.error(f"Error entering queue: {str(e)}")
            return False
            
    def enter_reservation_window(self) -> bool:
        """예매창 진입"""
        try:
            driver = self.driver_manager.get_driver()
            wait = self.driver_manager.get_wait()
            
            driver.switch_to.window(driver.window_handles[-1])
            
            wait.until(
                EC.presence_of_element_located((By.ID, "divBookSeat"))
            )
            
            logger.info("Successfully entered reservation window")
            return True
            
        except Exception as e:
            logger.error(f"Error entering reservation window: {str(e)}")
            return False
            
    def solve_captcha(self) -> Optional[str]:
        """캡차 해결"""
        try:
            driver = self.driver_manager.get_driver()
            
            captcha_element = driver.find_element(By.ID, "imgCaptcha")
            if not captcha_element:
                logger.info("No captcha found")
                return ""
                
            captcha_text = self.captcha_solver.solve(captcha_element)
            
            if captcha_text:
                captcha_input = driver.find_element(By.ID, "txtCaptcha")
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                
                confirm_button = driver.find_element(By.ID, "btnCaptchaOk")
                confirm_button.click()
                
                logger.info("Captcha solved successfully")
                return captcha_text
                
            return None
            
        except NoSuchElementException:
            logger.info("No captcha element found - skipping")
            return ""
            
        except Exception as e:
            logger.error(f"Error solving captcha: {str(e)}")
            return None
            
    def select_seats(self, reservation: Reservation) -> bool:
        """좌석 선택"""
        try:
            driver = self.driver_manager.get_driver()
            
            seat_frame = driver.find_element(By.ID, "ifrmSeat")
            driver.switch_to.frame(seat_frame)
            
            time.sleep(1)
            
            if not self.seat_selector:
                self.seat_selector = SeatSelector(driver)
            else:
                self.seat_selector.clear_selection()
                
            success = self.seat_selector.select_seats(reservation.seat_preference)
            
            driver.switch_to.default_content()
            
            return success
            
        except Exception as e:
            logger.error(f"Error selecting seats: {str(e)}")
            return False
            
    def handle_seat_conflict(self) -> bool:
        """좌석 충돌 처리"""
        try:
            driver = self.driver_manager.get_driver()
            
            driver.switch_to.default_content()
            
            try:
                alert_popup = driver.find_element(By.CLASS_NAME, "alert_popup")
                
                if "이미 선택된 좌석" in alert_popup.text:
                    close_button = alert_popup.find_element(By.CLASS_NAME, "btn_close")
                    close_button.click()
                    
                    logger.info("Handled seat conflict popup")
                    return True
                    
            except NoSuchElementException:
                pass
                
            return False
            
        except Exception as e:
            logger.error(f"Error handling seat conflict: {str(e)}")
            return False