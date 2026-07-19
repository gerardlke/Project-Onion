import { useState } from "react";


export default function NetworkNode({ 
  position, 
  color, 
  radius = 0.4,
  data, 
  activeNode, 
  setActiveNode 
}) {
  const [hovered, setHover] = useState(false);
  const isOpen = activeNode?.id === data.id;

  return (
    <mesh
      position={position}
      onClick={(e) => { e.stopPropagation(); setActiveNode(isOpen ? null : data); }}
      onPointerOver={(e) => { e.stopPropagation(); setHover(true); }}
      onPointerOut={() => setHover(false)}
    >
      <sphereGeometry args={[radius, 32, 32]} />
      <meshStandardMaterial color={(isOpen || hovered) ? '#fff065' : color} />
    </mesh>
  );
}
