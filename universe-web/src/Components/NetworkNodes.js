import { useState } from 'react';
import { Html } from '@react-three/drei';

export default function NetworkNode({
  position,
  color,
  data,
  activeNode,
  setActiveNode,
}) {
  const [hovered, setHover] = useState(false);
  const isOpen = activeNode?.id === data.id;

  return (
    <mesh
      position={position}
      onClick={(event) => {
        event.stopPropagation();
        setActiveNode(isOpen ? null : data);
      }}
      onPointerOver={(event) => {
        event.stopPropagation();
        setHover(true);
      }}
      onPointerOut={() => setHover(false)}
    >
      <sphereGeometry args={[0.4, 32, 32]} />
      <meshStandardMaterial color={hovered ? '#ffaa00' : color} />

      {isOpen && (
        <Html distanceFactor={6} position={[0, 0.6, 0]} center>
          <div
            style={{
              background: 'rgba(20, 20, 25, 0.95)',
              color: '#fff',
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid #4f46e5',
              boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
              whiteSpace: 'nowrap',
              fontFamily: 'sans-serif',
              fontSize: '14px',
              pointerEvents: 'auto',
            }}
          >
            <h4 style={{ margin: '0 0 4px 0', color: '#a5b4fc' }}>
              {data.label}
            </h4>
            <p style={{ margin: '0 0 8px 0', fontSize: '12px', opacity: 0.8 }}>
              {data.info}
            </p>
            <button
              onClick={(event) => {
                event.stopPropagation();
                setActiveNode(null);
              }}
              style={{
                background: '#4f46e5',
                color: 'white',
                border: 'none',
                padding: '4px 8px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '11px',
              }}
            >
              Close
            </button>
          </div>
        </Html>
      )}
    </mesh>
  );
}