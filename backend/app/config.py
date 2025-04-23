from pydantic_settings import BaseSettings

from typing import Optional


class Settings(BaseSettings):
    """アプリケーション設定"""
    # サービス設定
    APP_NAME: str = "Robot Backend"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    
    # ClassVarを使用してモデル外のフィールドをマーク、または型アノテーションを追加
    ROBOT_TRACKER_HOST: str = "localhost"  # または実際のIPアドレス
    ROBOT_TRACKER_PORT: str = "50051"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 設定をインスタンス化
settings = Settings()