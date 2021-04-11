from typing import Optional

from pydantic import BaseModel


class PingHost(BaseModel):
    host: str
    interval: float = 1.0
    interface: Optional[str] = None


class PingResult:
    def __init__(self, host, time):
        self.host = host
        self.time = float(time)
