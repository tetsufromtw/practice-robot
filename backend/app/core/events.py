import logging
from typing import Callable
from fastapi import FastAPI
from app.grpc_client.robot_client import client as robot_client
from app.websockets.manager import manager

logger = logging.getLogger(__name__)


def create_start_app_handler(app: FastAPI) -> Callable:
    """アプリケーション起動時の処理ハンドラーを作成"""
    
    async def start_app() -> None:
        """アプリケーション起動時に実行される処理"""
        logger.info("アプリケーションを起動中...")
        
        # robot-tracker gRPCサービスに接続 (awaitを使用)
        await robot_client.connect()
        
        # 位置更新のコールバック関数を設定
        robot_client.set_position_callback(manager.broadcast_position)
        
        # ロボット位置の受信を開始
        await robot_client.start_tracking()
        
        logger.info("アプリケーションの起動が完了しました")
    
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """アプリケーション終了時の処理ハンドラーを作成"""
    
    async def stop_app() -> None:
        """アプリケーション終了時に実行される処理"""
        logger.info("アプリケーションを終了中...")
        
        # ロボット位置の受信を停止
        await robot_client.stop_tracking()
        
        logger.info("アプリケーションの終了が完了しました")
    
    return stop_app