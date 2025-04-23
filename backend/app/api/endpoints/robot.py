from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from typing import Dict, Any

from app.websockets.manager import manager
from app.schemas.robot import RobotPosition

router = APIRouter()


@router.websocket("/ws/robot")
async def websocket_endpoint(websocket: WebSocket):
    """ロボット位置更新を受信するためのWebSocketエンドポイント"""
    await manager.connect(websocket)
    try:
        while True:
            # クライアントからのメッセージを待機（主にクライアントへの送信が目的）
            data = await websocket.receive_text()
            # クライアントから送信されたメッセージを処理可能だが、この例では無視
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """サービスの状態を取得"""
    return {
        "status": "running",
        "connections": len(manager.active_connections)
    }