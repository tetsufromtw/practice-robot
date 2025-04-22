import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import robot
from app.config import settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.core.errors import setup_error_handlers

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """創建 FastAPI 應用實例"""
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    
    # 設置 CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允許所有來源，生產環境中應限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 設置啟動和關閉事件
    application.add_event_handler(
        "startup",
        create_start_app_handler(application),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application),
    )
    
    # 設置錯誤處理
    setup_error_handlers(application)
    
    # 註冊路由
    application.include_router(robot.router, prefix=settings.API_PREFIX)
    
    return application


app = create_application()


if __name__ == "__main__":
    # 直接啟動時使用
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )