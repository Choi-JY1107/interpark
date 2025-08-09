from typing import List, Tuple, Optional
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from domain.entities import SeatPreference, SeatSelectionType, SeatDirection
import logging

logger = logging.getLogger(__name__)


class SeatSelector:
    def __init__(self, driver: Chrome):
        self.driver = driver
        self.selected_seats: List[WebElement] = []
        
    def select_seats(self, preference: SeatPreference) -> bool:
        """좌석 선택 수행"""
        try:
            available_seats = self._get_available_seats()
            
            if not available_seats:
                logger.warning("No available seats found")
                return False
                
            if preference.selection_type == SeatSelectionType.SMALL_GRAPE:
                return self._select_small_grape_pattern(available_seats, preference)
            elif preference.selection_type == SeatSelectionType.LARGE_GRAPE:
                return self._select_large_grape_pattern(available_seats, preference)
            else:
                return self._select_normal_pattern(available_seats, preference)
                
        except Exception as e:
            logger.error(f"Error selecting seats: {str(e)}")
            return False
            
    def _get_available_seats(self) -> List[WebElement]:
        """사용 가능한 좌석 조회"""
        try:
            return self.driver.find_elements(By.CSS_SELECTOR, ".seat_available")
        except Exception as e:
            logger.error(f"Failed to get available seats: {str(e)}")
            return []
            
    def _select_small_grape_pattern(self, seats: List[WebElement], 
                                   preference: SeatPreference) -> bool:
        """작은 포도알 패턴으로 좌석 선택 (최대 4석)"""
        sorted_seats = self._sort_seats_by_preference(seats, preference.direction)
        seats_to_select = min(4, preference.count)
        
        for seat in sorted_seats[:seats_to_select]:
            seat.click()
            self.selected_seats.append(seat)
            
        return len(self.selected_seats) > 0
        
    def _select_large_grape_pattern(self, seats: List[WebElement], 
                                   preference: SeatPreference) -> bool:
        """큰 포도알 패턴으로 좌석 선택 (최대 2석)"""
        sorted_seats = self._sort_seats_by_preference(seats, preference.direction)
        seats_to_select = min(2, preference.count)
        
        for seat in sorted_seats[:seats_to_select]:
            seat.click()
            self.selected_seats.append(seat)
            
        return len(self.selected_seats) > 0
        
    def _select_normal_pattern(self, seats: List[WebElement], 
                              preference: SeatPreference) -> bool:
        """일반 패턴으로 좌석 선택"""
        sorted_seats = self._sort_seats_by_preference(seats, preference.direction)
        
        for i in range(min(len(sorted_seats), preference.count)):
            sorted_seats[i].click()
            self.selected_seats.append(sorted_seats[i])
            
        return len(self.selected_seats) > 0
        
    def _sort_seats_by_preference(self, seats: List[WebElement], 
                                 direction: SeatDirection) -> List[WebElement]:
        """선호도에 따라 좌석 정렬"""
        seat_with_positions: List[Tuple[WebElement, int, int]] = []
        
        for seat in seats:
            try:
                row = int(seat.get_attribute('data-row') or '0')
                col = int(seat.get_attribute('data-col') or '0')
                seat_with_positions.append((seat, row, col))
            except (ValueError, TypeError):
                continue
                
        seat_with_positions.sort(
            key=lambda x: (x[1], x[2] if direction == SeatDirection.RIGHT else -x[2])
        )
        
        return [seat[0] for seat in seat_with_positions]
        
    def clear_selection(self):
        """선택한 좌석 초기화"""
        self.selected_seats.clear()