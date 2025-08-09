import threading
from datetime import datetime
from typing import Callable, Optional
import logging

from application.services.reservation_service import ReservationService
from application.dtos.reservation_dto import ReservationRequestDTO

logger = logging.getLogger(__name__)


class ReservationController:
    def __init__(self):
        self.service = ReservationService()
        self.is_running = False
        self._reservation_thread: Optional[threading.Thread] = None
        
    def start_reservation(self, 
                         request_dto: ReservationRequestDTO,
                         progress_callback: Callable[[str], None],
                         completion_callback: Callable[[bool, str], None]):
        """예매 시작"""
        if self.is_running:
            logger.warning("Reservation already in progress")
            return
            
        self.is_running = True
        self._reservation_thread = threading.Thread(
            target=self._run_reservation,
            args=(request_dto, progress_callback, completion_callback),
            daemon=True
        )
        self._reservation_thread.start()
        
    def stop_reservation(self):
        """예매 중지"""
        self.is_running = False
        if self._reservation_thread and self._reservation_thread.is_alive():
            self.service.cleanup()
            
    def _run_reservation(self,
                        request_dto: ReservationRequestDTO,
                        progress_callback: Callable[[str], None],
                        completion_callback: Callable[[bool, str], None]):
        """예매 실행"""
        try:
            target_time = datetime.strptime(
                f"{request_dto.date} {request_dto.target_time}",
                "%Y-%m-%d %H:%M:%S"
            )
            
            progress_callback("대기 중...")
            
            while datetime.now() < target_time and self.is_running:
                remaining = (target_time - datetime.now()).total_seconds()
                progress_callback(f"남은 시간: {remaining:.1f}초")
                
                if remaining > 60:
                    threading.Event().wait(10)
                else:
                    threading.Event().wait(0.1)
                    
            if not self.is_running:
                completion_callback(False, "예매가 중지되었습니다.")
                return
                
            progress_callback("티켓팅 시작!")
            
            response = self.service.make_reservation(request_dto, progress_callback)
            
            completion_callback(response.success, response.message)
            
        except Exception as e:
            logger.error(f"Controller error: {str(e)}")
            completion_callback(False, f"오류 발생: {str(e)}")
            
        finally:
            self.is_running = False