import json
from typing import Dict, List, Any
from fastapi import WebSocket
from app.schemas.robot import RobotPosition, WebSocketMessage


class ConnectionManager:
    """WebSocket接続を管理するクラス"""
    
    def __init__(self):
        # アクティブなWebSocket接続のリスト
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """新しいWebSocket接続を処理"""
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_event(websocket, "connected", {"message": "ロボットトラッカーに接続されました"})
    
    def disconnect(self, websocket: WebSocket):
        """WebSocket接続を切断"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_event(self, websocket: WebSocket, event: str, data: Any = None):
        """特定のWebSocket接続にイベントを送信"""
        message = WebSocketMessage(event=event, data=data)
        await websocket.send_text(json.dumps(message.dict()))
    
    async def broadcast_position(self, position: RobotPosition):
        """ロボットの位置をすべての接続クライアントにブロードキャスト"""
        if not self.active_connections:
            return
            
        message = WebSocketMessage(event="position_update", data=position)
        message_json = json.dumps(message.dict())
        
        # メッセージをすべての接続クライアントにブロードキャスト
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception:
                # 送信に失敗した場合、この接続を閉じる必要があるかもしれません
                # ここではエラーを無視して、他の接続に影響を与えないようにします
                pass


# グローバル接続マネージャーインスタンス
manager = ConnectionManager()