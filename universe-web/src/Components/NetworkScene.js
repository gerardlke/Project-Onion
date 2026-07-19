import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

import NetworkNode from './NetworkNodes';
import { createConceptNode, getTopicColor } from '../Data/network.js';


export default function NetworkScene({
  topics = [],
  conceptNodes = [],
  edges = [],
  activeNode,
  setActiveNode,
  onProcessingChange
}) {
  const [visibleNodes, setVisibleNodes] = useState([]);
  
  useEffect(() => {
    let cancelled = false;
    
    async function processNodes() {
      onProcessingChange?.(true);
      try {
        const nodes = await Promise.all(
          conceptNodes.map((concept) =>
            createConceptNode(concept, getTopicColor(concept.topic_id, topics))
          )
        );
        if (!cancelled) setVisibleNodes(nodes);
      } finally {
        if (!cancelled) onProcessingChange?.(false);
      }
    }

    if (conceptNodes.length > 0) {
      processNodes();
    } else {
      setVisibleNodes([]);
      onProcessingChange?.(false);
    }
    return () => { cancelled = true; };
  }, [conceptNodes, topics]);

  const nodePositionById = Object.fromEntries(
    visibleNodes.map((n) => [n.id, n.position])
  );

  return (
    <Canvas 
      camera={{ position: [0, 0, 7], fov: 60 }}
      gl={{ alpha: true }}
      style={{ background: 'transparent' }}
    >
      <ambientLight intensity={0.6} />
      <pointLight position={[10, 10, 10]} />

      {visibleNodes.map((node) => (
        <NetworkNode
          key={node.id}
          position={node.position}
          color={node.color}
          data={node}
          activeNode={activeNode}
          setActiveNode={setActiveNode}
        />
      ))}

      {/* Render one tube per edge between two concept nodes */}
      {edges.map((edge) => {
        const fromPos = nodePositionById[edge.source_id];
        const toPos = nodePositionById[edge.target_id];
        if (!fromPos || !toPos) return null;

        const from = new THREE.Vector3(...fromPos);
        const to = new THREE.Vector3(...toPos);
        const curve = new THREE.LineCurve3(from, to);

        return (
          <mesh key={`${edge.source_id}-${edge.target_id}`}>
            <tubeGeometry args={[curve, 8, 0.04, 6, false]} />
            <meshStandardMaterial
              color="white"
              opacity={0.35}
              transparent
            />
          </mesh>
        );
      })}

      {/* OrbitControls is scoped to this canvas, so page layout remains stable. */}
      <OrbitControls enableZoom makeDefault />
    </Canvas>
  );
}
