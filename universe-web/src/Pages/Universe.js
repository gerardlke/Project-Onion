import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../api';
import NetworkScene from '../Components/NetworkScene';


export default function Universe() {
  const navigate = useNavigate();
  const hasFetched = useRef(false);

  const [topics, setTopics] = useState([]);
  const [conceptNodes, setConceptNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function fetchUniverse() {
    setLoading(true);
    setError('');
    try {
      // Fetch nodes and relations in parallel.
      const [nodesResponse, relationsResponse] = await Promise.all([
        apiFetch('/universe/nodes?dimensions=3'),
        apiFetch('/universe/relations'),
      ]);

      if (!nodesResponse.ok || !relationsResponse.ok) {
        setError('Failed to load universe data. Please try refreshing.');
        return;
      }

      const nodesResult = await nodesResponse.json();
      const relationsResult = await relationsResponse.json();

      // Store unique topic names derived from nodes so NetworkScene can resolve colors without needing separate call
      const uniqueTopics = [
        ...new Map(
          (nodesResult.nodes || []).map((n) => [n.topic_name, { name: n.topic_name }])
        ).values(),
      ];
      setTopics(uniqueTopics);
      setConceptNodes(nodesResult.nodes || []);
      setEdges(relationsResult.relations || []);
      
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
    <div className="app">
      <section className="page-content">
        <h1>Your Universe</h1>
      </section>

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
        <button className="upload-button" onClick={() => navigate('/')}>
          ← Back to Upload
        </button>
        {/* Manual refresh that refetches nodes and relations */}
        <button
          className="upload-button"
          onClick={() => { hasFetched.current = false; fetchUniverse(); }}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Refresh Universe'}
        </button>
      </div>

      {/* Loading state during API call */}
      {loading && (
        <p className="status-message">Loading your universe...</p>
      )}

      {error && <p className="status-message">{error}</p>}

      {!loading && (
        <section className="network-panel" aria-label="Concept network">
          <NetworkScene
            topics={topics}
            conceptNodes={conceptNodes}
            edges={edges}
          />
        </section>
      )}
    </div>
  );
}
