import logging
from datetime import datetime
from typing import Callable, Optional

from domain.entities import (
    Reservation, Performance, SeatPreference, UserCredentials,
    SeatSelectionType, SeatDirection
)
from domain.use_cases import MakeReservationUseCase
from application.dtos.reservation_dto import ReservationRequestDTO, ReservationResponseDTO
from infrastructure.web_driver.driver_manager import WebDriverManager
from infrastructure.interpark.interpark_repository import InterparkRepository

logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(self):
        self.driver_manager = WebDriverManager()
        
    def make_reservation(self, 
                        request_dto: ReservationRequestDTO,
                        progress_callback: Optional[Callable[[str], None]] = None) -> ReservationResponseDTO:
        """예매 서비스 실행"""
        try:
            reservation = self._create_reservation_entity(request_dto)
            
            self.driver_manager.initialize()
            
            repository = InterparkRepository(self.driver_manager)
            use_case = MakeReservationUseCase(repository)
            
            success = use_case.execute(reservation, progress_callback)
            
            if success:
                return ReservationResponseDTO(
                    success=True,
                    message="좌석 선택이 완료되었습니다. 결제를 진행해주세요."
                )
            else:
                return ReservationResponseDTO(
                    success=False,
                    message="예매에 실패했습니다."
                )
                
        except Exception as e:
            logger.error(f"Reservation service error: {str(e)}")
            return ReservationResponseDTO(
                success=False,
                message="예매 중 오류가 발생했습니다.",
                error=str(e)
            )
        finally:
            self.cleanup()
            
    def cleanup(self):
        """리소스 정리"""
        try:
            self.driver_manager.quit()
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
            
    def _create_reservation_entity(self, dto: ReservationRequestDTO) -> Reservation:
        """DTO를 도메인 엔티티로 변환"""
        performance = Performance(
            name=dto.performance_name,
            url=dto.performance_url,
            date=dto.date,
            time=dto.time
        )
        
        seat_type_map = {
            "일반": SeatSelectionType.NORMAL,
            "작은 포도알": SeatSelectionType.SMALL_GRAPE,
            "큰 포도알": SeatSelectionType.LARGE_GRAPE
        }
        
        direction_map = {
            "오른쪽부터": SeatDirection.RIGHT,
            "왼쪽부터": SeatDirection.LEFT
        }
        
        seat_preference = SeatPreference(
            selection_type=seat_type_map.get(dto.seat_type, SeatSelectionType.NORMAL),
            direction=direction_map.get(dto.seat_direction, SeatDirection.RIGHT),
            count=dto.seat_count
        )
        
        credentials = None
        if dto.user_id and dto.user_password:
            credentials = UserCredentials(
                user_id=dto.user_id,
                password=dto.user_password
            )
            
        target_time = datetime.strptime(
            f"{dto.date} {dto.target_time}", 
            "%Y-%m-%d %H:%M:%S"
        )
        
        return Reservation(
            performance=performance,
            target_time=target_time,
            seat_preference=seat_preference,
            credentials=credentials
        )