import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { apiFetch } from '../Api';
import NetworkScene from '../Components/NetworkScene';
import './Universe.css';


export default function Universe() {
  const navigate = useNavigate();
  const hasFetched = useRef(false);

  const [topics, setTopics] = useState([]);
  const [conceptNodes, setConceptNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [activeNode, setActiveNode] = useState(null);

  const [loading, setLoading] = useState(false);
  const [nodesProcessing, setNodesProcessing] = useState(false);
  const [error, setError] = useState('');

  async function fetchUniverse() {
    setLoading(true);
    setError('');
    try {
      // Fetch topics, nodes, and relations in parallel.
      const [nodesResponse, relationsResponse, topicsResponse] = await Promise.all([
        apiFetch('/universe/nodes?dimensions=3'),
        apiFetch('/universe/relations'),
        apiFetch('/upload/get_topics')
      ]);

      if (!nodesResponse.ok || !relationsResponse.ok || !topicsResponse.ok) {
        setError('Failed to load universe data. Please try refreshing.');
        return;
      }

      const nodesResult = await nodesResponse.json();
      const relationsResult = await relationsResponse.json();

      // Normalizing topics response
      const topicsResult = await topicsResponse.json();
      function normalizeTopic(topic) {
        if (typeof topic === 'string') return { name: topic, description: '' };
        if (Array.isArray(topic)) return { name: topic[0] || '', description: topic[1] || '' };
        return { name: topic?.name || '', description: topic?.description || '' };
      }

      // Store unique topic names derived from nodes so NetworkScene can resolve colors without needing separate call
      const uniqueTopics = (topicsResult.topics || topicsResult.data || [])
        .map(normalizeTopic)
        .filter((t) => t.name);

      setTopics(uniqueTopics || []);
      setConceptNodes(nodesResult.nodes || []);
      setEdges(relationsResult.edges || []);
      
    } catch {
      setError('Universe service is unavailable. Please try again later.');
    } finally {
      setLoading(false);
    }
  }

  // Fetch once per session
  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;
    fetchUniverse();
  }, []);
  
  return (
    <div className="universe-page">
      {/* Full network panel */}
      {!loading && (
        <section className="network-panel-full" aria-label="Concept network">
          <NetworkScene
            topics={topics}
            conceptNodes={conceptNodes}
            edges={edges}
            activeNode={activeNode}
            setActiveNode={setActiveNode}
            onProcessingChange={setNodesProcessing}
          />
        </section>
      )}

      {/* Floating header overlay */}
      <header className="universe-header">
        <div className="universe-controls">
          <button className="universe-btn" onClick={() => navigate('/')}>
            ← Back to Upload
          </button>
          <button
            className="universe-btn universe-btn--accent"
            onClick={() => { hasFetched.current = false; fetchUniverse(); }}
            disabled={loading || nodesProcessing}
          >
            {(loading || nodesProcessing) ? 'Loading…' : 'Refresh Universe'}
          </button>
        </div>
      </header>

      {(loading || nodesProcessing) && (
        <p className="status-message universe-status">Loading your universe...</p>
      )}
      {error && (
        <p className="status-message universe-status">{error}</p>
      )}

      <div style={{
        position: 'fixed',
        top: 0,
        right: activeNode ? '0' : '-400px',
        width: '400px',
        height: '100vh',
        background: 'rgba(23, 30, 53, 0.95)',
        backdropFilter: 'blur(10px)',
        borderLeft: '1px solid rgba(255, 255, 255, 0.2)',
        color: '#fff',
        transition: 'right 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        boxShadow: '-10px 0 30px rgba(0,0,0,0.5)',
        zIndex: 3000,
        padding: '40px',
        boxSizing: 'border-box',
        fontFamily: "'Courier New', Courier, monospace",
        textAlign: 'left',
        pointerEvents: activeNode ? 'auto' : 'none'
      }}>
        {activeNode && (
          <>
            <h3 style={{ fontSize: '28px', margin: '0 0 10px', borderBottom: '1px solid rgba(255,255,255,0.2)', paddingBottom: '10px' }}>
              {activeNode.label}
            </h3>
            <p style={{ fontSize: '16px', color: '#a5b4fc', margin: '0 0 20px', fontWeight: 'bold' }}>
              Topic: {activeNode.topicName}
            </p>
            <div style={{ fontSize: '18px', lineHeight: '1.6', opacity: 0.9, marginBottom: '30px' }}>
              {activeNode.text || "No description available."}
            </div>
            <button
              onClick={() => setActiveNode(null)}
              style={{
                background: 'white', color: 'black', border: 'none',
                padding: '12px 24px', borderRadius: '8px', cursor: 'pointer',
                fontWeight: 'bold', fontFamily: 'inherit'
              }}
            >
              Close View
            </button>
          </>
        )}
      </div>
    </div>
  );
}
