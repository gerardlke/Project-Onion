import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

import NetworkNode from './NetworkNodes';
import { createConceptNode, getTopicColor } from '../Data/network.js';

// TODO: import NetworkEdge once you build that component


export default function NetworkScene({
  topics = [],
  conceptNodes = [],
  edges = [],
  activeNode,
  setActiveNode
}) {
  const [visibleNodes, setVisibleNodes] = useState([]);
  
  useEffect(() => {
    async function processNodes() {
      const nodes = await Promise.all(
        conceptNodes.map(async (concept) => 
          await createConceptNode(concept, getTopicColor(concept.topic_name, topics))
        )
      );
      setVisibleNodes(nodes);
    }

    if (conceptNodes.length > 0) {
      processNodes();
    }
  }, [conceptNodes, topics]);

  return (
    <Canvas camera={{ position: [0, 0, 7], fov: 60 }}>
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

      {/* OrbitControls is scoped to this canvas, so page layout remains stable. */}
      <OrbitControls enableZoom makeDefault />
    </Canvas>
  );
}
