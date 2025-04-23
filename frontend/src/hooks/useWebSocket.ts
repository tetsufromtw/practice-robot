import { useState, useEffect, useRef, useCallback } from 'react';
import { WebSocketMessage, RobotPosition } from '../types/websocket';

export const useWebSocket = (url: string) => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [position, setPosition] = useState<RobotPosition | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // 處理接收到的消息
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      if (message.event === 'position_update' && message.data) {
        setPosition(message.data as RobotPosition);
      } else if (message.event === 'connected') {
        console.log('WebSocket connected:', message.data);
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err);
      setError('訊息格式錯誤');
    }
  }, []);

  // 建立WebSocket連接
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('WebSocket connection established');
        setIsConnected(true);
        setError(null);
      };
      
      ws.onmessage = handleMessage;
      
      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        setError('連接發生錯誤');
        setIsConnected(false);
      };
      
      ws.onclose = () => {
        console.log('WebSocket connection closed');
        setIsConnected(false);
        // 嘗試在5秒後重新連接
        setTimeout(connect, 5000);
      };
      
      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('無法建立WebSocket連接');
      setIsConnected(false);
      // 嘗試在5秒後重新連接
      setTimeout(connect, 5000);
    }
  }, [url, handleMessage]);

  // 組件掛載時連接，卸載時斷開連接
  useEffect(() => {
    connect();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return { isConnected, position, error };
};