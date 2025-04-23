'use client';

import InfoPanel from '@/components/InfoPanel';
import MapCanvas from '@/components/MapCanvas';
import { useWebSocket } from '../hooks/useWebSocket';

export default function Home() {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://127.0.0.1:8000/api/ws/robot';
  const { isConnected, position, error } = useWebSocket(wsUrl);

  return (
<main className="h-screen bg-gray-100 p-4">
  <div className="flex w-full h-full bg-white rounded-lg overflow-hidden shadow">
    {/* Sidebar 區塊 */}
    <div className="w-[18%] p-4">
      <InfoPanel isConnected={isConnected} error={error} position={position} />
    </div>

    {/* 地圖主區域 */}
    <div className="flex-1 bg-gray-200 relative">
      <MapCanvas position={position} />
    </div>
  </div>
</main>

  );
}
