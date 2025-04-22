from pydantic import BaseModel
from typing import Optional


class RobotPosition(BaseModel):
    """機器人位置模型"""
    x: float
    y: float
    timestamp: int


class WebSocketMessage(BaseModel):
    """WebSocket 訊息模型"""
    event: str
    data: Optional[RobotPosition] = None
    
    class Config:
        schema_extra = {
            "example": {
                "event": "position_update",
                "data": {
                    "x": 123.45,
                    "y": 678.90,
                    "timestamp": 1617979797000
                }
            }
        }