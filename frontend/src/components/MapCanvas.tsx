'use client';

import React, { useEffect, useRef, useState } from 'react';

declare global {
  interface Window {
    svgJapan?: any;
  }
}

type Position = {
  x: number;
  y: number;
};

type MapCanvasProps = {
  position: Position | null;
};

export default function MapCanvas({ position }: MapCanvasProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [isInsideJapan, setIsInsideJapan] = useState(false);
  const MAX_X = 100;
  const MAX_Y = 100;

  useEffect(() => {
    if (typeof window !== 'undefined' && window.svgJapan && mapRef.current) {
      mapRef.current.innerHTML = '';
      window.svgJapan({
        element: '#japan-map',
        color: '#333',
        hoverColor: '#333',
        activeColor: '#333',
      });
    }
  }, []);

  useEffect(() => {
    if (!position) return;

    const svg = document.querySelector('#japan-map svg') as SVGSVGElement;
    if (!svg) return;

    const paths = svg.querySelectorAll('path');
    const pt = svg.createSVGPoint();
    pt.x = (position.x / MAX_X) * svg.viewBox.baseVal.width;
    pt.y = (position.y / MAX_Y) * svg.viewBox.baseVal.height;

    let inside = false;
    for (const path of paths) {
      const geom = path as unknown as SVGGeometryElement;
      if (geom.isPointInFill(pt)) {
        inside = true;
        break;
      }
    }

    setIsInsideJapan(inside);
  }, [position]);

  return (
    <div className="w-full h-full relative">
      <div ref={mapRef} id="japan-map" className="w-full h-full" />

      {position && (
        <div
          style={{
            position: 'absolute',
            zIndex: 50,
            fontSize: '48px',
            left: `${(position.x / MAX_X) * 100}%`,
            top: `${(position.y / MAX_Y) * 100}%`,
            transform: 'translate(-50%, -50%)',
          }}
        >
          🤖
        </div>
      )}
    </div>
  );
}
