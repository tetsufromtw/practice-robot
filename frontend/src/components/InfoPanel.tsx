'use client';

import React from 'react';

type Position = {
  x: number;
  y: number;
  timestamp: number;
};

type InfoPanelProps = {
  isConnected: boolean;
  error: string | null;
  position: Position | null;
};

export default function InfoPanel({ isConnected, error, position }: InfoPanelProps) {
  return (
    <div className="w-full max-w-sm p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold text-center mb-6">ロボット位置トラッカー</h1>

      {/* 接続状態 */}
      <div className="mb-6">
        <div className="flex items-center mb-2">
          <div className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="font-medium">状態: {isConnected ? '接続済み' : '未接続'}</span>
        </div>
        {error && <div className="text-red-500 text-sm">{error}</div>}
      </div>

      {/* 位置情報 */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-3">リアルタイム位置</h2>
        {position ? (
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">X 座標:</span>
              <span className="font-medium">{position.x.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Y 座標:</span>
              <span className="font-medium">{position.y.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">タイムスタンプ:</span>
              <span className="font-medium">{new Date(position.timestamp).toLocaleString()}</span>
            </div>
          </div>
        ) : (
          <div className="text-gray-500 text-center py-2">位置更新を待機中...</div>
        )}
      </div>
    </div>
  );
}
