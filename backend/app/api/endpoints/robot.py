from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from typing import Dict, Any

from app.websockets.manager import manager
from app.schemas.robot import RobotPosition

router = APIRouter()


@router.websocket("/ws/robot")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端點，用於接收機器人位置更新"""
    await manager.connect(websocket)
    try:
        while True:
            # 等待客戶端的消息，雖然我們主要是向客戶端發送消息
            data = await websocket.receive_text()
            # 這裡可以處理客戶端發送的消息，但在此例中我們忽略它們
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """獲取服務狀態"""
    return {
        "status": "running",
        "connections": len(manager.active_connections)
    }