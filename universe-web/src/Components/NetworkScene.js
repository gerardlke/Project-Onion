import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

import NetworkNode from './NetworkNodes';
import NetworkEdge from './NetworkEdge';

import { createConceptNode, getTopicColor } from '../Data/network.js';


export default function NetworkScene({
  topics = [],
  conceptNodes = [],
  edges = [],
  universeScale = 1,
  nodeScale = 1,
  activeNode,
  setActiveNode,
  activeEdge,
  setActiveEdge,
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

  const scaledNodes = visibleNodes.map((node) => ({
    ...node,
    position: node.position.map((v) => v * universeScale),
    radius: (node.radius ?? 0.4) * nodeScale,
  }));

  const nodePositionById = Object.fromEntries(
    scaledNodes.map((n) => [n.id, n.position])
  );

  return (
    <Canvas 
      camera={{ position: [0, 0, 7], fov: 60 }}
      gl={{ alpha: true }}
      style={{ background: 'transparent' }}
    >
      <ambientLight intensity={0.6} />
      <pointLight position={[10, 10, 10]} />

      {scaledNodes.map((node) => (
        <NetworkNode
          key={node.id}
          position={node.position}
          color={node.color}
          radius={node.radius}
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

        const isActive = activeEdge?.source_id === edge.source_id &&
                         activeEdge?.target_id === edge.target_id;

        return (
          <NetworkEdge
            key={`${edge.source_id}-${edge.target_id}`}
            edge={edge}
            fromPos={fromPos}
            toPos={toPos}
            isActive={isActive}
            onClickEdge={() => setActiveEdge(isActive ? null : edge)}
          />
        );
      })}

      {/* OrbitControls is scoped to this canvas, so page layout remains stable. */}
      <OrbitControls enableZoom makeDefault />
    </Canvas>
  );
}
