import asyncio
import logging
from typing import Optional, Callable, Any
import grpc.aio  # 使用 gRPC 的異步 IO 版本
from app.config import settings
from app.schemas.robot import RobotPosition

# 這些導入將在編譯 proto 後生效
from app.protos.robot import robot_pb2
from app.protos.robot import robot_pb2_grpc


logger = logging.getLogger(__name__)


class RobotTrackerClient:
    """機器人位置追蹤 gRPC 客戶端 - 非阻塞實現"""
    
    def __init__(self):
        self.host = settings.ROBOT_TRACKER_HOST
        self.port = settings.ROBOT_TRACKER_PORT
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[robot_pb2_grpc.RobotTrackerStub] = None
        self.position_callback: Optional[Callable[[RobotPosition], Any]] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._reconnect_delay = 1  # 初始重連延遲（秒）
        self._max_reconnect_delay = 30  # 最大重連延遲（秒）
    
    async def connect(self):
        """非阻塞連接到 gRPC 服務器"""
        if self.channel is not None:
            return
            
        target = f"{self.host}:{self.port}"
        logger.info(f"連接到 Robot Tracker gRPC 服務: {target}")
        
        # 添加連接選項
        options = [
            ('grpc.enable_http_proxy', 0),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.max_receive_message_length', 10 * 1024 * 1024),  # 10MB
            ('grpc.max_send_message_length', 10 * 1024 * 1024),     # 10MB
        ]
        
        # 使用異步通道和選項
        self.channel = grpc.aio.insecure_channel(target, options=options)
        self.stub = robot_pb2_grpc.RobotTrackerStub(self.channel)
        
        # 添加通道連接狀態檢查
        state = self.channel.get_state()
        logger.info(f"初始通道狀態: {state}")
        
        # 等待通道連接就緒或超時
        try:
            await asyncio.wait_for(
                self.channel.channel_ready(), 
                timeout=5.0  # 5秒超時
            )
            logger.info("通道已就緒")
        except asyncio.TimeoutError:
            logger.error("等待通道就緒超時")
    
    def set_position_callback(self, callback: Callable[[RobotPosition], Any]):
        """設置位置更新的回調函數"""
        self.position_callback = callback
    
    async def start_tracking(self):
        """開始追蹤機器人位置"""
        if self._running:
            return
            
        if self.stub is None:
            await self.connect()
            
        self._running = True
        # 創建追蹤任務但不等待它
        self._task = asyncio.create_task(self._track_robot())
        # 添加通道監控任務
        self._monitor_task = asyncio.create_task(self.monitor_channel_state())
        logger.info("位置追蹤任務已啟動")
    
    async def monitor_channel_state(self):
        """監控gRPC通道狀態"""
        while self._running and self.channel:
            state = self.channel.get_state()
            logger.info(f"gRPC通道當前狀態: {state}")
            
            # 嘗試過渡到READY狀態
            changed = await self.channel.channel_ready()
            if changed:
                logger.info(f"通道狀態已改變，新狀態: {self.channel.get_state()}")
            
            await asyncio.sleep(2)
    
    async def stop_tracking(self):
        """停止追蹤機器人位置"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None
            
        if self.channel:
            await self.channel.close()  # 異步關閉通道
            self.channel = None
            self.stub = None
        logger.info("位置追蹤任務已停止")
    
    async def _track_robot(self):
        """處理機器人位置流 - 非阻塞實現"""
        reconnect_delay = self._reconnect_delay
        logger.info("開始追蹤機器人位置流")
        
        while self._running:
            try:
                if self.stub is None:
                    logger.info("Stub不存在，嘗試連接...")
                    await self.connect()
                    
                logger.info(f"開始呼叫 TrackRobot gRPC 方法，目標: {self.host}:{self.port}")
                request = robot_pb2.TrackRequest()
                
                logger.debug("正在發送 TrackRobot 請求...")
                # 獲取流但不使用異步迭代器語法
                stream_call = self.stub.TrackRobot(request)
                
                while self._running:
                    try:
                        # 使用更基本的 read() 方法獲取下一個消息
                        response = await asyncio.wait_for(
                            stream_call.read(), 
                            timeout=10.0
                        )
                        
                        # 如果response是None，表示流已結束
                        if response is None:
                            logger.info("位置數據流已結束")
                            break
                            
                        logger.info(f"收到位置資料: x={response.x}, y={response.y}, ts={response.timestamp}")
                        
                        # 將 gRPC 響應轉換為我們的 Pydantic 模型
                        position = RobotPosition(
                            x=response.x,
                            y=response.y,
                            timestamp=response.timestamp
                        )
                        
                        # 如果設置了回調函數，則調用它
                        if self.position_callback:
                            try:
                                # 確保回調是協程或可調用對象
                                if asyncio.iscoroutinefunction(self.position_callback):
                                    await self.position_callback(position)
                                else:
                                    self.position_callback(position)
                            except Exception as e:
                                logger.error(f"位置更新回調錯誤: {e}")
                                
                    except asyncio.TimeoutError:
                        logger.error("讀取數據流超時")
                        # 檢查連接狀態
                        if self.channel and self.channel.get_state() != grpc.ChannelConnectivity.READY:
                            logger.info("通道不再就緒，中斷當前流")
                            break
                        # 繼續嘗試讀取
                        continue
                    except Exception as e:
                        logger.error(f"讀取流數據時出錯: {e}")
                        break
                
                # 如果到這裡，表示流已結束，但我們想繼續追蹤
                if self._running:
                    logger.info("位置流已結束或出錯，嘗試重新連接...")
                    # 關閉當前連接
                    if self.channel:
                        await self.channel.close()
                        self.channel = None
                        self.stub = None
                    await asyncio.sleep(reconnect_delay)  # 等待一段時間後重連
                    reconnect_delay = min(reconnect_delay * 2, self._max_reconnect_delay)
                
            except grpc.aio.AioRpcError as e:
                if self._running:
                    logger.error(f"gRPC 錯誤: {e.code()}: {e.details()}")
                    
                    # 關閉通道，準備重連
                    if self.channel:
                        await self.channel.close()
                        self.channel = None
                        self.stub = None
                    
                    # 使用指數退避策略進行重連
                    logger.info(f"將在 {reconnect_delay} 秒後重新連接...")
                    await asyncio.sleep(reconnect_delay)
                    
                    # 增加重連延遲，但不超過最大值
                    reconnect_delay = min(reconnect_delay * 2, self._max_reconnect_delay)
                else:
                    break
            except Exception as e:
                logger.error(f"追蹤機器人時出現未知錯誤: {e}")
                if self._running:
                    await asyncio.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, self._max_reconnect_delay)
                else:
                    break
        
        logger.info("位置追蹤任務結束")


# 全局客戶端實例
client = RobotTrackerClient()