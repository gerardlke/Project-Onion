import { useState } from "react";


export default function NetworkNode({ position, color, data, activeNode, setActiveNode }) {
  const [hovered, setHover] = useState(false);
  const isOpen = activeNode?.id === data.id;

  return (
    <mesh
      position={position}
      onClick={(e) => { e.stopPropagation(); setActiveNode(isOpen ? null : data); }}
      onPointerOver={(e) => { e.stopPropagation(); setHover(true); }}
      onPointerOut={() => setHover(false)}
    >
      <sphereGeometry args={[data.radius, 32, 32]} />
      <meshStandardMaterial color={(isOpen || hovered) ? '#ffaa00' : color} />
    </mesh>
  );
}
