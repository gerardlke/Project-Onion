import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { useSpring, animated } from '@react-spring/three';
import * as THREE from 'three';

import NetworkNode from './NetworkNodes';
import NetworkEdge from './NetworkEdge';

import { createConceptNode, getTopicColor } from '../Data/network.js';


function SpringNode({ node, index, ...nodeProps }) {
  const { position } = useSpring({
    from: { position: [0, 0, 0] },
    to: { position: node.position },
    delay: index * 80,  // 80ms stagger between nodes
    config: { mass: 1.2, tension: 120, friction: 22 },
  });

  return (
    <animated.group position={position}>
      <NetworkNode
        position={[0, 0, 0]}
        color={node.color}
        radius={node.radius}
        data={node}
        {...nodeProps}
      />
    </animated.group>
  );
}


function Starfield() {
  const ref = useRef();

  const positions = useMemo(() => {
    const arr = new Float32Array(1000 * 3);
    for (let i = 0; i < 1000; i++) {
      // Distribute randomly inside a large sphere of radius 60
      const r = 30 + Math.random() * 30;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = r * Math.cos(phi);
    }
    return arr;
  }, []);

  // Each star gets a slightly different brightness
  const sizes = useMemo(() => {
    const arr = new Float32Array(1000);
    for (let i = 0; i < 1000; i++) arr[i] = 0.04 + Math.random() * 0.08;
    return arr;
  }, []);

  useFrame((_, delta) => {
    if (ref.current) {
      ref.current.rotation.y += delta * 0.012;
      ref.current.rotation.x += delta * 0.004;
    }
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-size"
          args={[sizes, 1]}
        />
      </bufferGeometry>
      <pointsMaterial
        color="#ffffff"
        size={0.06}
        sizeAttenuation
        transparent
        opacity={0.55}
        depthWrite={false}
      />
    </points>
  );
}


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

      <Starfield />

      {scaledNodes.map((node, index) => (
        <SpringNode
          key={node.id}
          node={node}
          index={index}
          activeNode={activeNode}
          setActiveNode={setActiveNode}
        />
      ))}
      
      {/* Render one tube per edge between two concept nodes */}
      {edges.map((edge) => {
        const fromPos = nodePositionById[edge.source_id];
        const toPos = nodePositionById[edge.target_id];
        if (!fromPos || !toPos) return null;
        
        const sourceNode = visibleNodes.find((n) => n.id === edge.source_id);
        const targetNode = visibleNodes.find((n) => n.id === edge.target_id);

        const isActive = (activeEdge?.source_id === edge.source_id) && (activeEdge?.target_id === edge.target_id);
        
        console.log("visibleNodes", visibleNodes[edge.source_id], visibleNodes[edge.target_id])
        return (
          <NetworkEdge
            key={`${edge.source_id}-${edge.target_id}`}
            edge={edge}
            fromPos={fromPos}
            toPos={toPos}
            fromColor={sourceNode?.color ?? '#4f46e5'}
            toColor={targetNode?.color ?? '#06b6d4'}
            isActive={isActive}
            onClickEdge={() => {
              if (isActive) { setActiveEdge(null); return; }
              setActiveEdge({
                ...edge,
                source_label: sourceNode?.label ?? edge.source_id,
                target_label: targetNode?.label ?? edge.target_id,
              });
            }}
          />
        );
      })}

      {/* OrbitControls is scoped to this canvas, so page layout remains stable. */}
      <OrbitControls enableZoom makeDefault />
    </Canvas>
  );
}
