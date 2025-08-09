import logging
from typing import Callable, Optional
from domain.entities import Reservation
from domain.repositories.reservation_repository import ReservationRepository

logger = logging.getLogger(__name__)


class MakeReservationUseCase:
    def __init__(self, repository: ReservationRepository):
        self.repository = repository
        self.max_retry_attempts = 100
        
    def execute(self, reservation: Reservation, 
                progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        try:
            self._log_progress("대기열 진입 시도 중...", progress_callback)
            
            if not self.repository.enter_queue(reservation):
                self._log_progress("대기열 진입 실패", progress_callback)
                return False
                
            self._log_progress("예매창 진입 중...", progress_callback)
            
            if not self.repository.enter_reservation_window():
                self._log_progress("예매창 진입 실패", progress_callback)
                return False
                
            self._log_progress("보안문자 처리 중...", progress_callback)
            
            captcha_result = self.repository.solve_captcha()
            if captcha_result is None:
                self._log_progress("보안문자 처리 실패", progress_callback)
                return False
                
            self._log_progress("좌석 선택 중...", progress_callback)
            
            for attempt in range(self.max_retry_attempts):
                if self.repository.select_seats(reservation):
                    self._log_progress("좌석 선택 성공!", progress_callback)
                    return True
                    
                if not self.repository.handle_seat_conflict():
                    continue
                    
                self._log_progress(f"좌석 선택 재시도 중... ({attempt + 1}/{self.max_retry_attempts})", 
                                 progress_callback)
                
            self._log_progress("좌석 선택 실패 (최대 재시도 횟수 초과)", progress_callback)
            return False
            
        except Exception as e:
            logger.error(f"예매 중 오류 발생: {str(e)}")
            self._log_progress(f"오류 발생: {str(e)}", progress_callback)
            return False
            
    def _log_progress(self, message: str, callback: Optional[Callable[[str], None]]):
        logger.info(message)
        if callback:
            callback(message)