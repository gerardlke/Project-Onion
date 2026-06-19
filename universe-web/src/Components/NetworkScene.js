import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import NetworkNode from './NetworkNodes';
import { createTopicNode } from '../Data/network.js';

/**
 * Renders the 3D universe canvas.
 *
 * The canvas is intentionally mounted even when there are no nodes. Each topic
 * returned by the API is converted into a node. Documents are uploaded from the
 * node detail popover.
 *
 * @param {Object} props
 * @param {Array<{name: string, description: string}>} props.topics - Topics to show as nodes.
 * @param {Object<string, Array<Object>>} props.documentsByTopic - Uploaded documents keyed by topic name.
 * @param {(topicName: string, file: File) => Promise<void>} props.onUploadDocument - Upload handler.
 * @param {Object<string, string>} props.uploadMessages - Upload messages keyed by topic name.
 * @returns {JSX.Element}
 */
export default function NetworkScene({
  topics = [],
  documentsByTopic = {},
  onUploadDocument,
  uploadMessages = {},
}) {
  const [activeNode, setActiveNode] = useState(null);

  // Derive renderable scene data from React state instead of storing duplicate node state.
  const visibleNodes = topics.map((topic, index) => createTopicNode(topic, index));

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
          documents={documentsByTopic[node.topicName] || []}
          activeNode={activeNode}
          setActiveNode={setActiveNode}
          onUploadDocument={onUploadDocument}
          uploadMessage={uploadMessages[node.topicName] || ''}
        />
      ))}

      {/* OrbitControls is scoped to this canvas, so page layout remains stable. */}
      <OrbitControls enableZoom makeDefault />
    </Canvas>
  );
}
