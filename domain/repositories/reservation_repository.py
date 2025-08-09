from abc import ABC, abstractmethod
from typing import Optional
from domain.entities import Reservation


class ReservationRepository(ABC):
    @abstractmethod
    def enter_queue(self, reservation: Reservation) -> bool:
        """대기열 진입"""
        pass
    
    @abstractmethod
    def enter_reservation_window(self) -> bool:
        """예매창 진입"""
        pass
    
    @abstractmethod
    def solve_captcha(self) -> Optional[str]:
        """캡차 해결"""
        pass
    
    @abstractmethod
    def select_seats(self, reservation: Reservation) -> bool:
        """좌석 선택"""
        pass
    
    @abstractmethod
    def handle_seat_conflict(self) -> bool:
        """좌석 충돌 처리"""
        pass