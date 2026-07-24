import React, { useRef, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../Api';

import './Upload.css';
import CursorGlow from '../Components/CursorGlow';


function TopicDropdown({ topics, selectedTopic, onSelect }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // Close on outside click
  useEffect(() => {
    function handleOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    if (open) document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, [open]);

  const selectedLabel = topics.find((t) => t.name === selectedTopic)?.name
    || 'No topics yet - create one first!';

  return (
    <div className="topic-dropdown" ref={ref}>
      {/* Selected slot — always visible, click to open */}
      <button
        type="button"
        className={`topic-dropdown-selected ${open ? 'topic-dropdown-selected--open' : ''}`}
        onClick={() => topics.length > 0 && setOpen((o) => !o)}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <span>{selectedLabel}</span>
        <svg
          className={`topic-dropdown-chevron ${open ? 'topic-dropdown-chevron--open' : ''}`}
          width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      {/* Animated options panel */}
      <div className={`topic-dropdown-panel ${open ? 'topic-dropdown-panel--open' : ''}`} role="listbox">
        {topics.map((t) => (
          <button
            key={t.name}
            type="button"
            role="option"
            aria-selected={t.name === selectedTopic}
            className={`topic-dropdown-option ${t.name === selectedTopic ? 'topic-dropdown-option--active' : ''}`}
            onClick={() => { onSelect(t.name); setOpen(false); }}
          >
            <span className="topic-dropdown-option-name">{t.name}</span>
            {t.description && (
              <span className="topic-dropdown-option-desc">{t.description}</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function Upload({ loggedInUser, onLogout, onTopicsChange }) {
  const navigate = useNavigate();

  const [topics, setTopics] = useState([]);
  const [newTopicName, setNewTopicName] = useState('');
  const [newTopicDescription, setNewTopicDescription] = useState('');
  const [topicMessage, setTopicMessage] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [uploadMessages, setUploadMessages] = useState({});

  // Track which topics are currently uploading to show a loading state.
  const [uploadingTopics, setUploadingTopics] = useState({});
  const [uploadProgress, setUploadProgress] = useState(null);

  // Topic creation card
  const [showNewTopicCard, setShowNewTopicCard] = useState(false);

  function normalizeTopic(topic) {
    if (typeof topic === 'string') return { name: topic, description: '' };
    if (Array.isArray(topic)) return { name: topic[0] || '', description: topic[1] || '' };
    return { name: topic?.name || '', description: topic?.description || '' };
  }

  useEffect(() => {
    async function loadTopics() {
      try {
        const response = await apiFetch('/upload/get_topics');
        if (!response.ok) throw new Error('Topic request failed');
        const result = await response.json();
        const loaded = (result.topics || result.data || [])
          .map(normalizeTopic)
          .filter((t) => t.name);
        setTopics(loaded);
        onTopicsChange?.(loaded); 
        if (loaded.length > 0) setSelectedTopic(loaded[0].name);
      } catch {
        setTopicMessage('Could not load topics. You can still create a new one.');
      }
    }
    loadTopics();
  }, [onTopicsChange]);

  async function handleCreateTopic(event) {
    event.preventDefault();
    setTopicMessage('');
    try {
      const response = await apiFetch('/upload/new_topic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newTopicName, description: newTopicDescription }),
      });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        setTopicMessage(errorBody?.detail || 'Topic creation failed.');
        return;
      }
      const result = await response.json();
      if (!result.success) { setTopicMessage('Topic creation failed.'); return; }
      const created = { name: result.name || newTopicName, description: result.description || newTopicDescription };
      
      setTopics((current) => {
        const updated = [...current, created];
        onTopicsChange?.(updated);
        return updated;
      
      });
      setSelectedTopic(created.name);
      setNewTopicName('');
      setNewTopicDescription('');
      setTopicMessage(`Created topic: ${created.name}`);

      setShowNewTopicCard(false);
    } catch {
      setTopicMessage('Topic service is unavailable. Please try again later.');
    }
  }

  async function handleUploadDocument(event) {
    const file = event.target.files[0];
    if (!file || !selectedTopic) return;
    event.target.value = '';

    // Show loading state for this topic during the upload call.
    setUploadingTopics((current) => ({ ...current, [selectedTopic]: true }));
    setUploadProgress({ percent: 0, message: 'Starting upload...' });
    setUploadMessages((current) => ({ ...current, [selectedTopic]: 'Uploading...' }));

    const formData = new FormData();
    formData.append('file', file);
    formData.append('topic_name', selectedTopic);

    try {
      const response = await apiFetch('/upload/new_document', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        setUploadMessages((current) => ({
          ...current,
          [selectedTopic]: errorBody?.detail || 'Upload failed.',
        }));
        setUploadProgress(null);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        // Keep the last incomplete line in the buffer.
        buffer = lines.pop();

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data:')) continue;

          try {
            const payload = JSON.parse(trimmed.slice(5).trim());

            if (typeof payload.percent === 'number') {
              setUploadProgress({
                percent: payload.percent,
                message: payload.message || '',
              });
            }

            // Backend signals completion with percent === 100 or a success flag.
            if (payload.percent === 100 || payload.success === true) {
              setUploadMessages((current) => ({
                ...current,
                [selectedTopic]: `Uploaded ${file.name} successfully.`,
              }));
            }
          } catch {
            // Malformed line — ignore and continue reading.
          }
        }
      }
      
    } catch {
      setUploadMessages((current) => ({
        ...current,
        [selectedTopic]: 'Upload service is unavailable. Please try again later.',
      }));
    } finally {
      // Always clear loading state when the call settles.
      setUploadingTopics((current) => ({ ...current, [selectedTopic]: false }));
      setTimeout(() => setUploadProgress(null), 1200);
    }
  }

  const isUploading = Object.values(uploadingTopics).some(Boolean);

  return (
    <div className="upload-page">
      <CursorGlow />

      {/* Loading overlay — unchanged */}
      {uploadProgress !== null && (
        <div className="upload-overlay">
          <div className="upload-progress-card">
            <p className="upload-progress-message">{uploadProgress.message}</p>
            <div className="upload-progress-track">
              <div className="upload-progress-fill" style={{ width: `${uploadProgress.percent}%` }} />
            </div>
            <p className="upload-progress-percent">{uploadProgress.percent}%</p>
          </div>
        </div>
      )}

      {/* Page header */}
      <div className="upload-header">
        <p className="upload-wordmark">Project Onion</p>
        <h1 className="upload-title">Your Knowledge Universe</h1>
        <p className="upload-subtitle">
          Organise your notes into topics and upload documents to grow your semantic universe.
        </p>
      </div>

      {/* Main glass card */}
      <div className="upload-card">

        {/* Topic selector row */}
        <div className="upload-field-label">Topic</div>
        <div className="upload-topic-row">
          <TopicDropdown
            topics={topics}
            selectedTopic={selectedTopic}
            onSelect={setSelectedTopic}
          />

          {/* New Topic button */}
          <button
            className="upload-new-topic-btn"
            onClick={() => { setTopicMessage(''); setShowNewTopicCard(true); }}
            type="button"
          >
            + New
          </button>
        </div>

        {/* Divider */}
        <div className="upload-divider" />

        {/* Upload document section */}
        <div className="upload-field-label">Document</div>
        <label className={`upload-file-btn ${isUploading || topics.length === 0 ? 'upload-file-btn--disabled' : ''}`}>
          {isUploading ? 'Uploading…' : 'Choose File to Upload'}
          <input
            className="file-input"
            type="file"
            onChange={handleUploadDocument}
            disabled={isUploading || topics.length === 0}
          />
        </label>

        {/* Status messages per topic */}
        {Object.entries(uploadMessages).map(([topic, message]) =>
          message ? (
            <p key={topic} className="upload-status-msg">
              <span className="upload-status-topic">{topic}</span> {message}
            </p>
          ) : null
        )}

        {/* Topic message (creation feedback) */}
        {topicMessage && (
          <p className="upload-status-msg">{topicMessage}</p>
        )}
      </div>

      {/* View Universe CTA */}
      <button className="upload-cta-btn" onClick={() => navigate('/universe')}>
        View Universe →
      </button>

      {/* New Topic modal */}
      {showNewTopicCard && (
        <div className="upload-modal-overlay" role="dialog" aria-modal="true">
          <div className="upload-modal-card">
            <div className="upload-modal-header">
              <div>
                <p className="upload-modal-eyebrow">New Topic</p>
                <h2 className="upload-modal-title">Create a topic</h2>
              </div>
              <button
                className="upload-modal-close"
                onClick={() => setShowNewTopicCard(false)}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleCreateTopic}>
              <div className="upload-modal-field">
                <label className="upload-field-label" htmlFor="topic-name">Name</label>
                <input
                  id="topic-name"
                  className="upload-input"
                  type="text"
                  value={newTopicName}
                  onChange={(e) => setNewTopicName(e.target.value)}
                  placeholder="e.g. CS2040S"
                  required
                />
              </div>

              <div className="upload-modal-field">
                <label className="upload-field-label" htmlFor="topic-desc">Description</label>
                <input
                  id="topic-desc"
                  className="upload-input"
                  type="text"
                  value={newTopicDescription}
                  onChange={(e) => setNewTopicDescription(e.target.value)}
                  placeholder="e.g. Data Structures and Algorithms"
                  required
                />
              </div>

              {topicMessage && <p className="upload-status-msg">{topicMessage}</p>}

              <button type="submit" className="upload-cta-btn upload-cta-btn--modal">
                Create Topic
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}