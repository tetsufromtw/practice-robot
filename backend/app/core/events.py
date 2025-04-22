import logging
from typing import Callable
from fastapi import FastAPI
from app.grpc_client.robot_client import client as robot_client
from app.websockets.manager import manager

logger = logging.getLogger(__name__)


def create_start_app_handler(app: FastAPI) -> Callable:
    """創建應用程式啟動處理函數"""
    
    async def start_app() -> None:
        """應用程式啟動時執行的操作"""
        logger.info("應用程式啟動中...")
        
        # 連接到 robot-tracker gRPC 服務 (使用 await)
        await robot_client.connect()
        
        # 設置位置更新的回調函數
        robot_client.set_position_callback(manager.broadcast_position)
        
        # 開始接收機器人位置
        await robot_client.start_tracking()
        
        logger.info("應用程式啟動完成")
    
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """創建應用程式關閉處理函數"""
    
    async def stop_app() -> None:
        """應用程式關閉時執行的操作"""
        logger.info("應用程式關閉中...")
        
        # 停止接收機器人位置
        await robot_client.stop_tracking()
        
        logger.info("應用程式關閉完成")
    
    return stop_app