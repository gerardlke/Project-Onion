import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../Api';

import './Upload.css';


export default function Upload({ loggedInUser, onLogout }) {
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
        if (loaded.length > 0) setSelectedTopic(loaded[0].name);
      } catch {
        setTopicMessage('Could not load topics. You can still create a new one.');
      }
    }
    loadTopics();
  }, []);

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
      
      setTopics((current) => [...current, created]);
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
    <div className="app">
      {/* Full screen loading overlay*/}
      {uploadProgress !== null && (
        <div className="upload-overlay">
          <div className="upload-progress-card">
            <p className="upload-progress-message">{uploadProgress.message}</p>
            <div className="upload-progress-track">
              <div
                className="upload-progress-fill"
                style={{ width: `${uploadProgress.percent}%` }}
              />
            </div>
            <p className="upload-progress-percent">{uploadProgress.percent}%</p>
          </div>
        </div>
      )}

      <section className="page-content">
        <h1>Project Onion</h1>
        <p>Choose a topic and upload documents to grow your semantic universe.</p>
      </section>

      <section className="topic-panel" aria-label="Upload document">
        <div className="topic-row">
          <div className="topic-select-label">
            <label htmlFor="topic-select">Topic</label>
            <select
              id="topic-select"
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              disabled={topics.length === 0}
            >
              {topics.length === 0
                ? <option>No topics yet</option>
                : topics.map((t) => <option key={t.name} value={t.name}>{t.name}</option>)
              }
            </select>
          </div>

          {/* New Topic button to open topic card */}
          <button
            className="new-topic-btn"
            onClick={() => { setTopicMessage(''); setShowNewTopicCard(true); }}
          >
            + New Topic
          </button>
        </div>

        {topics.length > 0 && (
          <label className="upload-button">
            {isUploading ? 'Uploading…' : 'Upload Document'}
            <input
              className="file-input"
              type="file"
              onChange={handleUploadDocument}
              disabled={isUploading}
            />
          </label>
        )}

        {Object.entries(uploadMessages).map(([topic, message]) =>
          message ? (
            <p key={topic} className="status-message">
              <strong>{topic}:</strong> {message}
            </p>
          ) : null
        )}
      </section>

      <button className="upload-button" onClick={() => navigate('/universe')}>
        View Universe →
      </button>

      {/* New Topic card that appears over page */}
      {showNewTopicCard && (
        <div className="popup-overlay" role="dialog" aria-modal="true" aria-label="Create new topic">
          <div className="popup new-topic-card">
            <button
              className="popup-close"
              onClick={() => setShowNewTopicCard(false)}
              aria-label="Close"
            >
              ×
            </button>
            <h2>New Topic</h2>
            <p>Give your topic a name and a short description.</p>
            <form className="new-topic-form" onSubmit={handleCreateTopic}>
              <label htmlFor="topic-name">Name</label>
              <input
                id="topic-name"
                type="text"
                value={newTopicName}
                onChange={(e) => setNewTopicName(e.target.value)}
                placeholder="e.g. CS1101s"
                required
              />
              <label htmlFor="topic-desc">Description</label>
              <input
                id="topic-desc"
                type="text"
                value={newTopicDescription}
                onChange={(e) => setNewTopicDescription(e.target.value)}
                placeholder="e.g. Programming Methodology 1"
                required
              />
              {topicMessage && <p className="status-message">{topicMessage}</p>}
              <button type="submit" className="upload-button popup-upload-button">
                Create Topic
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}