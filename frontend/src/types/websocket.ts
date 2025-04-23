// WebSocket消息類型定義
export interface RobotPosition {
    x: number;
    y: number;
    timestamp: number;
  }
  
  export interface WebSocketMessage {
    event: string;
    data: RobotPosition | { message: string } | null;
  }