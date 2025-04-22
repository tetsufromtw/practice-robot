import json
from typing import Dict, List, Any
from fastapi import WebSocket
from app.schemas.robot import RobotPosition, WebSocketMessage


class ConnectionManager:
    """管理 WebSocket 連接的類"""
    
    def __init__(self):
        # 活躍的 WebSocket 連接列表
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """處理新的 WebSocket 連接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_event(websocket, "connected", {"message": "Connected to robot tracker"})
    
    def disconnect(self, websocket: WebSocket):
        """斷開 WebSocket 連接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_event(self, websocket: WebSocket, event: str, data: Any = None):
        """發送事件到特定的 WebSocket 連接"""
        message = WebSocketMessage(event=event, data=data)
        await websocket.send_text(json.dumps(message.dict()))
    
    async def broadcast_position(self, position: RobotPosition):
        """廣播機器人位置給所有連接的客戶端"""
        if not self.active_connections:
            return
            
        message = WebSocketMessage(event="position_update", data=position)
        message_json = json.dumps(message.dict())
        
        # 將訊息廣播給所有連接的客戶端
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception:
                # 如果發送失敗，我們可能需要關閉這個連接
                # 但這裡我們只是忽略錯誤，避免影響其他連接
                pass


# 全局連接管理器實例
manager = ConnectionManager()