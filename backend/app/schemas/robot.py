from pydantic import BaseModel
from typing import Optional


class RobotPosition(BaseModel):
    """ロボットの位置モデル"""
    x: float
    y: float
    timestamp: int


class WebSocketMessage(BaseModel):
    """WebSocketメッセージモデル"""
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