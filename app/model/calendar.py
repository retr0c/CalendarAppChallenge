from dataclasses import dataclass
from datetime import datetime

@dataclass
class Reminder:
    EMAIL = "email"
    SYSTEM = "system"
    
    date_time: datetime
    type: str = EMAIL
    
    def __str__(self):
        return f"Reminder on {self.date_time} of type {self.type}"
    
