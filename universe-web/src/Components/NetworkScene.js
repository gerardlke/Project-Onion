import { useMemo, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Line, OrbitControls } from '@react-three/drei';
import NetworkNode from './NetworkNodes';
import { links, nodes } from '../Data/network.js';

export default function NetworkScene() {
  const [activeNode, setActiveNode] = useState(null);

  const nodesById = useMemo(
    () => new Map(nodes.map((node) => [node.id, node])),
    [],
  );

  return (
    <Canvas camera={{ position: [0, 0, 7], fov: 60 }}>
      <ambientLight intensity={0.6} />
      <pointLight position={[10, 10, 10]} />

      {links.map(([fromId, toId]) => {
        const fromNode = nodesById.get(fromId);
        const toNode = nodesById.get(toId);

        if (!fromNode || !toNode) {
          return null;
        }

        return (
          <Line
            key={`${fromId}-${toId}`}
            points={[fromNode.position, toNode.position]}
            color="#4b5563"
            lineWidth={1.5}
            dashed={false}
          />
        );
      })}

      {nodes.map((node) => (
        <NetworkNode
          key={node.id}
          position={node.position}
          color={node.color}
          data={node}
          activeNode={activeNode}
          setActiveNode={setActiveNode}
        />
      ))}

      <OrbitControls enableZoom makeDefault />
    </Canvas>
  );
}
