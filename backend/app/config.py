from pydantic_settings import BaseSettings

from typing import Optional


class Settings(BaseSettings):
    """應用程式配置設定"""
    # 服務配置
    APP_NAME: str = "Robot Backend"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    
    # 使用 ClassVar 標註非模型欄位，或者添加類型標註
    ROBOT_TRACKER_HOST: str = "localhost"  # 或者實際的 IP 地址
    ROBOT_TRACKER_PORT: str = "50051"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 實例化設置
settings = Settings()