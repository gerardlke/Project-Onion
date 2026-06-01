import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import NetworkNode from './NetworkNodes';
import { createUploadedFileNode } from '../Data/network.js';

/**
 * Renders the 3D universe canvas.
 *
 * The canvas is intentionally mounted even when there are no nodes. Before a
 * file is selected, the scene is blank. After upload, the file is converted
 * into the first network node.
 *
 * @param {Object} props
 * @param {File|null} [props.uploadedFile=null] - Latest file selected by the user.
 * @returns {JSX.Element}
 */
export default function NetworkScene({ uploadedFile = null }) {
  const [activeNode, setActiveNode] = useState(null);

  // Derive renderable scene data from React state instead of storing duplicate node state.
  const visibleNodes = uploadedFile
    ? [createUploadedFileNode(uploadedFile.name)]
    : [];

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
