import asyncio
import logging
from typing import Optional, Callable, Any
import grpc.aio  # gRPCの非同期IOバージョンを使用
from app.config import settings
from app.schemas.robot import RobotPosition

# これらのインポートはprotoをコンパイル後に有効になります
from app.protos.robot import robot_pb2
from app.protos.robot import robot_pb2_grpc


logger = logging.getLogger(__name__)


class RobotTrackerClient:
    """ロボット位置追跡用gRPCクライアント - 非ブロッキング実装"""
    
    def __init__(self):
        self.host = settings.ROBOT_TRACKER_HOST
        self.port = settings.ROBOT_TRACKER_PORT
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[robot_pb2_grpc.RobotTrackerStub] = None
        self.position_callback: Optional[Callable[[RobotPosition], Any]] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._reconnect_delay = 1  # 初期再接続遅延（秒）
        self._max_reconnect_delay = 30  # 最大再接続遅延（秒）
    
    async def connect(self):
        """非ブロッキングでgRPCサーバーに接続"""
        if self.channel is not None:
            return
            
        target = f"{self.host}:{self.port}"
        logger.info(f"Robot Tracker gRPCサービスに接続: {target}")
        
        # 接続オプションを追加
        options = [
            ('grpc.enable_http_proxy', 0),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.max_receive_message_length', 10 * 1024 * 1024),  # 10MB
            ('grpc.max_send_message_length', 10 * 1024 * 1024),     # 10MB
        ]
        
        # 非同期チャネルとオプションを使用
        self.channel = grpc.aio.insecure_channel(target, options=options)
        self.stub = robot_pb2_grpc.RobotTrackerStub(self.channel)
        
        # チャネル接続状態を確認
        state = self.channel.get_state()
        logger.info(f"初期チャネル状態: {state}")
        
        # チャネルが準備完了になるまで待機、またはタイムアウト
        try:
            await asyncio.wait_for(
                self.channel.channel_ready(), 
                timeout=5.0  # 5秒タイムアウト
            )
            logger.info("チャネルが準備完了")
        except asyncio.TimeoutError:
            logger.error("チャネル準備完了の待機中にタイムアウト")
    
    def set_position_callback(self, callback: Callable[[RobotPosition], Any]):
        """位置更新のコールバック関数を設定"""
        self.position_callback = callback
    
    async def start_tracking(self):
        """ロボット位置の追跡を開始"""
        if self._running:
            return
            
        if self.stub is None:
            await self.connect()
            
        self._running = True
        # 追跡タスクを作成（待機しない）
        self._task = asyncio.create_task(self._track_robot())
        # チャネル監視タスクを追加
        self._monitor_task = asyncio.create_task(self.monitor_channel_state())
        logger.info("位置追跡タスクが開始されました")
    
    async def monitor_channel_state(self):
        """gRPCチャネルの状態を監視"""
        while self._running and self.channel:
            state = self.channel.get_state()
            logger.info(f"gRPCチャネルの現在の状態: {state}")
            
            # READY状態への遷移を試みる
            changed = await self.channel.channel_ready()
            if changed:
                logger.info(f"チャネル状態が変更されました。新しい状態: {self.channel.get_state()}")
            
            await asyncio.sleep(2)
    
    async def stop_tracking(self):
        """ロボット位置の追跡を停止"""
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
            await self.channel.close()  # 非同期でチャネルを閉じる
            self.channel = None
            self.stub = None
        logger.info("位置追跡タスクが停止しました")
    
    async def _track_robot(self):
        """ロボット位置ストリームを処理 - 非ブロッキング実装"""
        reconnect_delay = self._reconnect_delay
        logger.info("ロボット位置ストリームの追跡を開始")
        
        while self._running:
            try:
                if self.stub is None:
                    logger.info("Stubが存在しません。接続を試みます...")
                    await self.connect()
                    
                logger.info(f"TrackRobot gRPCメソッドを呼び出し開始。ターゲット: {self.host}:{self.port}")
                request = robot_pb2.TrackRequest()
                
                logger.debug("TrackRobotリクエストを送信中...")
                # ストリームを取得（非同期イテレータ構文は使用しない）
                stream_call = self.stub.TrackRobot(request)
                
                while self._running:
                    try:
                        # より基本的なread()メソッドを使用して次のメッセージを取得
                        response = await asyncio.wait_for(
                            stream_call.read(), 
                            timeout=10.0
                        )
                        
                        # responseがNoneの場合、ストリームが終了したことを示す
                        if response is None:
                            logger.info("位置データストリームが終了しました")
                            break
                            
                        logger.info(f"位置データを受信: x={response.x}, y={response.y}, ts={response.timestamp}")
                        
                        # gRPCレスポンスをPydanticモデルに変換
                        position = RobotPosition(
                            x=response.x,
                            y=response.y,
                            timestamp=response.timestamp
                        )
                        
                        # コールバック関数が設定されている場合、それを呼び出す
                        if self.position_callback:
                            try:
                                # コールバックがコルーチンまたは呼び出し可能オブジェクトであることを確認
                                if asyncio.iscoroutinefunction(self.position_callback):
                                    await self.position_callback(position)
                                else:
                                    self.position_callback(position)
                            except Exception as e:
                                logger.error(f"位置更新コールバックエラー: {e}")
                                
                    except asyncio.TimeoutError:
                        logger.error("データストリームの読み取りがタイムアウト")
                        # 接続状態を確認
                        if self.channel and self.channel.get_state() != grpc.ChannelConnectivity.READY:
                            logger.info("チャネルが準備完了ではなくなりました。現在のストリームを中断します")
                            break
                        # 読み取りを続行
                        continue
                    except Exception as e:
                        logger.error(f"ストリームデータの読み取り中にエラーが発生: {e}")
                        break
                
                # ここに到達した場合、ストリームが終了したことを意味しますが、追跡を続行したい
                if self._running:
                    logger.info("位置ストリームが終了またはエラーが発生。再接続を試みます...")
                    # 現在の接続を閉じる
                    if self.channel:
                        await self.channel.close()
                        self.channel = None
                        self.stub = None
                    await asyncio.sleep(reconnect_delay)  # 一定時間待機後に再接続
                    reconnect_delay = min(reconnect_delay * 2, self._max_reconnect_delay)
                
            except grpc.aio.AioRpcError as e:
                if self._running:
                    logger.error(f"gRPCエラー: {e.code()}: {e.details()}")
                    
                    # チャネルを閉じて再接続の準備
                    if self.channel:
                        await self.channel.close()
                        self.channel = None
                        self.stub = None
                    
                    # 指数バックオフ戦略を使用して再接続
                    logger.info(f"{reconnect_delay}秒後に再接続を試みます...")
                    await asyncio.sleep(reconnect_delay)
                    
                    # 再接続遅延を増加（最大値を超えないようにする）
                    reconnect_delay = min(reconnect_delay * 2, self._max_reconnect_delay)
                else:
                    break
            except Exception as e:
                logger.error(f"ロボット追跡中に未知のエラーが発生: {e}")
                if self._running:
                    await asyncio.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, self._max_reconnect_delay)
                else:
                    break
        
        logger.info("位置追跡タスクが終了しました")


# グローバルクライアントインスタンス
client = RobotTrackerClient()