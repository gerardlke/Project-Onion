import { useState } from "react";
import { Html } from "@react-three/drei";

/**
 * Interactive 3D node rendered inside the network canvas.
 *
 * The node is responsible for hover styling and for toggling its own detail
 * popover. Parent scene state tracks the currently active node so only one
 * popover is open at a time.
 *
 * @param {Object} props
 * @param {[number, number, number]} props.position - 3D coordinates for the node.
 * @param {string} props.color - Default material color.
 * @param {{id: string|number, label: string, info: string, topicName: string}} props.data - Display data for the node.
 * @param {Array<Object>} props.documents - Documents uploaded to this topic.
 * @param {{id: string|number}|null} props.activeNode - Node currently showing details.
 * @param {Function} props.setActiveNode - Setter provided by the parent scene.
 * @param {(topicName: string, file: File) => Promise<void>} props.onUploadDocument - Upload handler.
 * @param {string} props.uploadMessage - Upload status for this topic.
 * @returns {JSX.Element}
 */
export default function NetworkNode({
  position,
  color,
  data,
  documents,
  activeNode,
  setActiveNode,
  onUploadDocument,
  uploadMessage,
}) {
  const [hovered, setHover] = useState(false);
  const isOpen = activeNode?.id === data.id;

  async function handleDocumentChange(event) {
    const file = event.target.files[0];
    if (!file || !onUploadDocument) {
      return;
    }

    await onUploadDocument(data.topicName, file);
    event.target.value = '';
  }

  return (
    <mesh
      position={position}
      onClick={(event) => {
        // Stop canvas-level interactions from also handling the node click.
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
      <meshStandardMaterial color={hovered ? "#ffaa00" : color} />

      {/* Html anchors ordinary DOM content to this mesh's position in 3D space. */}
      {isOpen && (
        <Html distanceFactor={6} position={[0, 0.6, 0]} center>
          <div
            style={{
              background: "rgba(20, 20, 25, 0.95)",
              color: "#fff",
              padding: "12px 16px",
              borderRadius: "8px",
              border: "1px solid #4f46e5",
              boxShadow: "0 4px 20px rgba(0,0,0,0.5)",
              fontFamily: "sans-serif",
              fontSize: "14px",
              pointerEvents: "auto",
              minWidth: '260px',
              maxWidth: '340px',
              whiteSpace: 'normal',
            }}
          >
            <h4 style={{ margin: "0 0 4px 0", color: "#a5b4fc" }}>
              {data.label}
            </h4>
            <p style={{ margin: "0 0 8px 0", fontSize: "12px", opacity: 0.8 }}>
              {data.info}
            </p>
            <label
              style={{
                display: 'block',
                margin: '10px 0 8px',
                fontSize: '12px',
                fontWeight: 700,
              }}
            >
              Upload document
              <input
                type="file"
                onChange={handleDocumentChange}
                style={{ display: 'block', marginTop: '6px', width: '100%' }}
              />
            </label>
            {uploadMessage && (
              <p style={{ margin: '0 0 8px', fontSize: '12px', color: '#bfdbfe' }}>
                {uploadMessage}
              </p>
            )}
            <div style={{ margin: '8px 0 10px', textAlign: 'left' }}>
              <strong style={{ color: '#a5b4fc', fontSize: '12px' }}>Documents</strong>
              {documents.length > 0 ? (
                <ul style={{ margin: '6px 0 0', paddingLeft: '18px', fontSize: '12px' }}>
                  {documents.map((document) => (
                    <li key={`${document.document_id}-${document.filename}`}>
                      {document.filename}
                    </li>
                  ))}
                </ul>
              ) : (
                <p style={{ margin: '6px 0 0', fontSize: '12px', opacity: 0.75 }}>
                  No documents uploaded yet.
                </p>
              )}
            </div>
            <button
              onClick={(event) => {
                event.stopPropagation();
                setActiveNode(null);
              }}
              style={{
                background: "#4f46e5",
                color: "white",
                border: "none",
                padding: "4px 8px",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "11px",
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
