from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ReservationRequestDTO:
    performance_name: str
    performance_url: str
    date: str
    time: str
    target_time: str
    seat_type: str
    seat_direction: str
    seat_count: int
    user_id: Optional[str] = None
    user_password: Optional[str] = None
    
    
@dataclass
class ReservationResponseDTO:
    success: bool
    message: str
    error: Optional[str] = None