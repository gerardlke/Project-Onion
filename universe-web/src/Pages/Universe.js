import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { apiFetch } from '../Api';
import { getTopicColor, fetchNodeDetail } from '../Data/network.js';
import NetworkScene from '../Components/NetworkScene';
import AiChatBot from '../Components/AiChatBot';
import './Universe.css';


function TopicLegendRow({ topic, color }) {
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const tooltipPosRef = useRef({ x: 0, y: 0 });

  function handleMouseMove(e) {
    const newX = e.clientX + 14;
    const newY = e.clientY - 8;
    if (
      Math.abs(newX - tooltipPosRef.current.x) > 2 ||
      Math.abs(newY - tooltipPosRef.current.y) > 2
    ) {
      tooltipPosRef.current = { x: newX, y: newY };
      setTooltipPos({ x: newX, y: newY });
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        cursor: topic.description ? 'default' : undefined,
        position: 'relative',
      }}
      onMouseEnter={() => topic.description && setTooltipVisible(true)}
      onMouseLeave={() => setTooltipVisible(false)}
      onMouseMove={handleMouseMove}
    >
      <span style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        flexShrink: 0,
        background: color,
        boxShadow: `0 0 6px ${color}`,
      }} />
      <span style={{
        fontSize: '12px',
        color: 'rgba(255,255,255,0.70)',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        maxWidth: '120px',
      }}>
        {topic.name}
      </span>

      {tooltipVisible && topic.description && (
        <div style={{
          position: 'fixed',
          left: tooltipPos.x,
          top: tooltipPos.y,
          zIndex: 9999,
          background: 'rgba(8, 13, 28, 0.97)',
          border: '1px solid rgba(255,255,255,0.14)',
          borderRadius: '8px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
          padding: '8px 12px',
          maxWidth: '200px',
          fontFamily: "'Courier New', Courier, monospace",
          fontSize: '11px',
          color: 'rgba(255,255,255,0.75)',
          lineHeight: '1.5',
          pointerEvents: 'none',
          whiteSpace: 'normal',
        }}>
          {topic.description}
        </div>
      )}
    </div>
  );
}

export default function Universe() {
  const navigate = useNavigate();
  const hasFetched = useRef(false);

  const [topics, setTopics] = useState([]);
  const [conceptNodes, setConceptNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [activeNode, setActiveNode] = useState(null);
  const [activeEdge, setActiveEdge] = useState(null);

  const [loading, setLoading] = useState(false);
  const [nodesProcessing, setNodesProcessing] = useState(false);
  const [error, setError] = useState('');

  const [universeScale, setUniverseScale] = useState(1.7);
  const [nodeScale, setNodeScale] = useState(0.7);
  const [showEdges, setShowEdges] = useState(true);

  const [isMobile, setIsMobile] = useState(() => window.innerWidth <= 640);

  useEffect(() => {
    function handleResize() {
      setIsMobile(window.innerWidth <= 640);
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  async function handleSetActiveNode(node) {
    if (!node) {
      setActiveNode(null);
      return;
    }

    setActiveNode(node);

    try {
      const detail = await fetchNodeDetail(node.id);
      setActiveNode((current) => {
        if (!current || current.id !== node.id) return current;
        return {
          ...current,
          label: detail.concept,
          text: detail.text ?? 'No description available.',
          topicName: detail.topic_name ?? current.topicName,
        };
      });
    } catch {
      setActiveNode((current) => {
        if (!current || current.id !== node.id) return current;
        return { ...current, text: 'Could not load concept detail.' };
      });
    }
  }

  async function handleSetActiveEdge(edge) {
    if (!edge) {
      setActiveEdge(null);
      return;
    }

    setActiveEdge(edge);

    try {
      const [source_detail, target_detail] = await Promise.all([
        fetchNodeDetail(edge.source_id),
        fetchNodeDetail(edge.target_id)
      ]);

      setActiveEdge((current) => {
        if (!current || current.id !== edge.id) {
          return current;
        }
        return {
          ...current,
          source_label: source_detail.concept,
          target_label: target_detail.concept,
        };
      });

    } catch (error) {
      console.error("Failed to load edge details:", error);
      setActiveEdge((current) => {
        if (!current || current.id !== edge.id) {
          return current;
        }
        return {
          ...current,
        };
      });
    }
  }

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

      function normalizeTopic(topic, index) {
        const assignedId = index + 1; 

        if (typeof topic === 'string') 
          return { id: assignedId, name: topic, description: '' };
        if (Array.isArray(topic)) 
          return { id: assignedId, name: topic[0] || '', description: topic[1] || '' };
        
        return { id: topic?.id ?? assignedId, name: topic?.name || '', description: topic?.description || '' };
      }

      // Store unique topic names derived from nodes so NetworkScene can resolve colors without needing separate call
      const uniqueTopics = (topicsResult.topics || topicsResult.data || [])
        .map((topic, index) => normalizeTopic(topic, index))
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

  const cardBase = {
    position: 'fixed',
    width: '340px',
    height: '44vh',
    background: 'rgba(255, 255, 255, 0.04)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.10)',
    borderRadius: '20px',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.45)',
    color: '#fff',
    fontFamily: "'Courier New', Courier, monospace",
    padding: '24px 26px',
    boxSizing: 'border-box',
    transition: 'right 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease',
    zIndex: 3000,
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    overflowY: 'auto',
  };

  // Node card anchors to bottom-right.
  const nodeCardStyle = {
    ...cardBase,
    ...(isMobile ? {
      left: 0,
      right: 0,
      bottom: activeNode ? '0' : '-60vh',
      width: '100%',
      height: '50vh',
      borderRadius: '20px 20px 0 0',
      transition: 'bottom 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease',
    } : {
      right: activeNode ? '20px' : '-380px',
      bottom: '20px',
      width: '340px',
      height: '44vh',
      borderRadius: '20px',
      transition: 'right 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease',
    }),
    opacity: activeNode ? 1 : 0,
    pointerEvents: activeNode ? 'auto' : 'none',
  };

  // Edge card anchors to top-right, below the header buttons.
  const edgeCardStyle = {
    ...cardBase,
    ...(isMobile ? {
      left: 0,
      right: 0,
      top: activeEdge ? '0' : '-60vh',
      width: '100%',
      height: '50vh',
      borderRadius: '0 0 20px 20px',
      transition: 'top 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease',
    } : {
      right: activeEdge ? '20px' : '-380px',
      top: '72px',
      width: '340px',
      height: '44vh',
      borderRadius: '20px',
      transition: 'right 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.35s ease',
    }),
    opacity: activeEdge ? 1 : 0,
    pointerEvents: activeEdge ? 'auto' : 'none',
  };

  // Shared close button style.
  const closeBtn = {
    marginTop: 'auto',
    alignSelf: 'flex-start',
    background: 'rgba(255,255,255,0.08)',
    border: '1px solid rgba(255,255,255,0.15)',
    borderRadius: '8px',
    color: 'white',
    cursor: 'pointer',
    fontFamily: 'inherit',
    fontSize: '12px',
    fontWeight: 'bold',
    letterSpacing: '0.06em',
    padding: '8px 14px',
    transition: 'background 0.15s',
  };

  const labelStyle = {
    fontSize: '11px',
    fontWeight: 'bold',
    letterSpacing: '0.1em',
    opacity: 0.5,
    margin: 0,
    textTransform: 'uppercase',
  };

  const bodyStyle = {
    fontSize: '13px',
    lineHeight: '1.65',
    opacity: 0.85,
    margin: 0,
    flexGrow: 1,
    overflowY: 'auto',
  };

  const sliderStyle = {
    width: '100%',
    appearance: 'none',
    WebkitAppearance: 'none',
    height: '3px',
    borderRadius: '999px',
    background: 'rgba(255,255,255,0.15)',
    outline: 'none',
    cursor: 'pointer',
    accentColor: '#6378ff',
  };
  
  return (
    <div className="universe-page">
      {/* Full network panel */}
      {!loading && (
        <section className="network-panel-full" aria-label="Concept network">
          <NetworkScene
            topics={topics}
            conceptNodes={conceptNodes}
            edges={showEdges ? edges : []}
            universeScale={universeScale}
            nodeScale={nodeScale}
            activeNode={activeNode}
            setActiveNode={handleSetActiveNode}
            activeEdge={activeEdge}
            setActiveEdge={handleSetActiveEdge}
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
        <div className="universe-loading" role="status" aria-label="Loading universe">
          <div className="universe-spinner" />
          <p className="universe-loading-text">Building your universe…</p>
        </div>
      )}
      {error && (
        <p className="status-message universe-status">{error}</p>
      )}

      <div style={nodeCardStyle}>
        {activeNode && (
          <>
            <p style={labelStyle}>Concept · {activeNode.topicName}</p>
            <h3 style={{ fontSize: '18px', margin: 0, fontWeight: 'bold', lineHeight: 1.3 }}>
              {activeNode.label}
            </h3>
            {/* Colour bar tied to the node's topic colour */}
            <div style={{ width: '32px', height: '2px', background: activeNode.color, borderRadius: '2px' }} />
            <p style={bodyStyle}>
              {activeNode.text === null
                ? <span style={{ opacity: 0.4, fontStyle: 'italic', fontSize: '12px' }}>
                    Loading…
                  </span>
                : activeNode.text || 'No description available.'
              }
            </p>
            <button style={closeBtn} onClick={() => setActiveNode(null)}>
              CLOSE
            </button>
          </>
        )}
      </div>

      {/* Edge detail card; slides in from top-right */}
      <div style={edgeCardStyle}>
        {activeEdge && (
          <>
            <p style={labelStyle}>Relationship</p>
            <h3 style={{ fontSize: '15px', margin: 0, fontWeight: 'bold', lineHeight: 1.4 }}>
              <span style={{ color: '#fde68a' }}>
                {activeEdge.source_label || activeEdge.source_id}
              </span>
              <span style={{ opacity: 0.4, margin: '0 8px', fontSize: '13px' }}>→</span>
              <span style={{ color: '#fde68a' }}>
                {activeEdge.target_label || activeEdge.target_id}
              </span>
            </h3>
            {activeEdge.relation_type && (
              <p style={{ ...labelStyle, opacity: 0.7, color: '#a5b4fc' }}>
                {activeEdge.relation_type}
              </p>
            )}
            <div style={{ width: '32px', height: '2px', background: '#facc15', borderRadius: '2px' }} />
            <p style={bodyStyle}>
              {activeEdge.explanation || 'No explanation available.'}
            </p>
            {typeof activeEdge.weight === 'number' && (
              <p style={{ ...labelStyle, opacity: 0.3 }}>
                Weight {activeEdge.weight.toFixed(3)}
              </p>
            )}
            <button style={closeBtn} onClick={() => setActiveEdge(null)}>
              CLOSE
            </button>
          </>
        )}
      </div>

      {/* Universe controls */}
      <div style={{
        position: 'fixed',
        bottom: 'calc(22px + 56px + 16px)',
        left: '20px',
        zIndex: 3000,
        background: 'rgba(255, 255, 255, 0.04)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.10)',
        borderRadius: '16px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        padding: '18px 22px',
        display: isMobile ? 'none' : 'flex',
        flexDirection: 'column',
        gap: '14px',
        minWidth: '200px',
        fontFamily: "'Courier New', Courier, monospace",
      }}>
        {/* Panel label */}
        <p style={{
          margin: 0,
          fontSize: '10px',
          fontWeight: 'bold',
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: 'rgba(255,255,255,0.35)',
        }}>
          Universe Controls
        </p>

        {/* Spread slider */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label style={{ fontSize: '11px', color: 'rgba(255,255,255,0.6)', letterSpacing: '0.04em' }}>
              Spread
            </label>
            <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.35)', fontVariantNumeric: 'tabular-nums' }}>
              {universeScale.toFixed(1)}
            </span>
          </div>
          <input
            type="range"
            min="0.5"
            max="4"
            step="0.1"
            value={universeScale}
            onChange={(e) => setUniverseScale(parseFloat(e.target.value))}
            style={sliderStyle}
          />
        </div>

        {/* Node size slider */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label style={{ fontSize: '11px', color: 'rgba(255,255,255,0.6)', letterSpacing: '0.04em' }}>
              Node Size
            </label>
            <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.35)', fontVariantNumeric: 'tabular-nums' }}>
              {nodeScale.toFixed(1)}
            </span>
          </div>
          <input
            type="range"
            min="0.3"
            max="2.5"
            step="0.1"
            value={nodeScale}
            onChange={(e) => setNodeScale(parseFloat(e.target.value))}
            style={sliderStyle}
          />
        </div>

        {/* Edge visibility toggle */}
        <button
          onClick={() => setShowEdges((prev) => !prev)}
          style={{
            background: showEdges ? 'rgba(99, 120, 255, 0.15)' : 'rgba(255,255,255,0.05)',
            border: showEdges
              ? '1px solid rgba(99, 120, 255, 0.45)'
              : '1px solid rgba(255,255,255,0.12)',
            borderRadius: '8px',
            color: showEdges ? '#a5b4fc' : 'rgba(255,255,255,0.4)',
            cursor: 'pointer',
            fontFamily: 'inherit',
            fontSize: '11px',
            fontWeight: 'bold',
            letterSpacing: '0.08em',
            padding: '8px 12px',
            textAlign: 'left',
            transition: 'background 0.2s, border-color 0.2s, color 0.2s',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: showEdges ? '#6378ff' : 'rgba(255,255,255,0.2)',
            flexShrink: 0,
            transition: 'background 0.2s',
          }} />
          {showEdges ? 'Edges Visible' : 'Edges Hidden'}
        </button>
      </div>

      {topics.length > 0 && !isMobile && (
        <div style={{
          position: 'fixed',
          bottom: 'calc(22px + 56px + 16px + 180px + 12px)',
          left: '20px',
          zIndex: 3000,
          background: 'rgba(255, 255, 255, 0.04)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.10)',
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          padding: '16px 20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          minWidth: '160px',
          maxWidth: '200px',
          fontFamily: "'Courier New', Courier, monospace",
        }}>
          <p style={{
            margin: 0,
            fontSize: '10px',
            fontWeight: 'bold',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'rgba(255,255,255,0.35)',
          }}>
            Topics
          </p>

          {/* Scrollable list with max height shows 3 topics */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            maxHeight: '108px',
            overflowY: topics.length > 3 ? 'auto' : 'visible',
            paddingRight: topics.length > 3 ? '4px' : '0',
          }} className="topics-legend-scroll">
            {topics.map((topic) => (
              <TopicLegendRow
                key={topic.id ?? topic.name}
                topic={topic}
                color={getTopicColor(topic.id)}
              />
            ))}
          </div>
        </div>
      )}

      <AiChatBot />
    </div>
  );
}
