from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from enum import Enum


class SeatSelectionType(Enum):
    NORMAL = "normal"
    SMALL_GRAPE = "small_grape"
    LARGE_GRAPE = "large_grape"


class SeatDirection(Enum):
    RIGHT = "right"
    LEFT = "left"


@dataclass
class Performance:
    name: str
    url: str
    date: str
    time: str
    
    def __post_init__(self):
        if not self.name or not self.url:
            raise ValueError("Performance name and URL are required")


@dataclass
class SeatPreference:
    selection_type: SeatSelectionType
    direction: SeatDirection
    count: int = 1
    
    def __post_init__(self):
        if self.count < 1 or self.count > 4:
            raise ValueError("Seat count must be between 1 and 4")


@dataclass
class UserCredentials:
    user_id: Optional[str] = None
    password: Optional[str] = None
    
    @property
    def is_provided(self) -> bool:
        return bool(self.user_id and self.password)


@dataclass
class Reservation:
    performance: Performance
    target_time: datetime
    seat_preference: SeatPreference
    credentials: Optional[UserCredentials] = None
    
    def __post_init__(self):
        if self.target_time <= datetime.now():
            raise ValueError("Target time must be in the future")