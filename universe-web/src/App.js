import React, { useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import NetworkScene from './Components/NetworkScene';
import Login from './Login/Login';
import Register from './Login/Register';

/**
 * Root application component.
 *
 * Responsibilities:
 * - Hold top-level UI state for login, upload modal visibility, and the latest uploaded file.
 * - Render login/register routes before a user is signed in.
 * - Keep the network canvas mounted after login so the universe is visible before and after upload.
 */
function App() {
  const [loggedInUser, setLoggedInUser] = useState('');
  const [topics, setTopics] = useState([]);
  const [documentsByTopic, setDocumentsByTopic] = useState({});
  const [newTopicName, setNewTopicName] = useState('');
  const [newTopicDescription, setNewTopicDescription] = useState('');
  const [topicMessage, setTopicMessage] = useState('');
  const [uploadMessages, setUploadMessages] = useState({});

  function normalizeTopic(topic) {
    if (typeof topic === 'string') {
      return { name: topic, description: '' };
    }

    if (Array.isArray(topic)) {
      return { name: topic[0] || '', description: topic[1] || '' };
    }

    return {
      name: topic?.name || '',
      description: topic?.description || '',
    };
  }

  useEffect(() => {
    if (!loggedInUser) {
      return;
    }

    async function loadTopics() {
      try {
        const response = await fetch('/upload/get_topics');
        if (!response.ok) {
          throw new Error('Topic request failed');
        }

        const result = await response.json();
        const loadedTopics = (result.topics || result.data || [])
          .map(normalizeTopic)
          .filter((topic) => topic.name);
        setTopics(loadedTopics);
      } catch (error) {
        setTopicMessage('Could not load topics. You can still create a new one.');
      }
    }

    loadTopics();
  }, [loggedInUser]);

  async function handleCreateTopic(event) {
    event.preventDefault();
    setTopicMessage('');

    try {
      const response = await fetch('/upload/new_topic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newTopicName,
          description: newTopicDescription,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        setTopicMessage(errorBody?.detail || 'Topic creation failed.');
        return;
      }

      const result = await response.json();
      if (!result.success) {
        setTopicMessage('Topic creation failed.');
        return;
      }

      const createdTopic = {
        name: result.name || newTopicName,
        description: result.description || newTopicDescription,
      };

      setTopics((currentTopics) => [...currentTopics, createdTopic]);
      setNewTopicName('');
      setNewTopicDescription('');
      setTopicMessage(`Created topic: ${createdTopic.name}`);
    } catch (error) {
      setTopicMessage('Topic service is unavailable. Please try again later.');
    }
  }

  async function handleUploadDocument(topicName, file) {
    setUploadMessages((currentMessages) => ({
      ...currentMessages,
      [topicName]: 'Uploading document...',
    }));

    const formData = new FormData();
    formData.append('file', file);
    formData.append('topic_name', topicName);

    try {
      const response = await fetch('/upload/new_document', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        setUploadMessages((currentMessages) => ({
          ...currentMessages,
          [topicName]: errorBody?.detail || 'File upload failed.',
        }));
        return;
      }

      const result = await response.json();
      if (!result.success) {
        setUploadMessages((currentMessages) => ({
          ...currentMessages,
          [topicName]: 'File upload failed.',
        }));
        return;
      }

      const uploadedDocument = {
        topic: result.topic || topicName,
        filename: result.filename || file.name,
        content_type: result.content_type || file.type,
        size_mb: result.size_mb,
        document_id: result.document_id,
        num_chunks: result.num_chunks,
        concepts: result.concepts,
      };

      setDocumentsByTopic((currentDocuments) => ({
        ...currentDocuments,
        [topicName]: [...(currentDocuments[topicName] || []), uploadedDocument],
      }));
      setUploadMessages((currentMessages) => ({
        ...currentMessages,
        [topicName]: `Uploaded ${uploadedDocument.filename}`,
      }));
    } catch (error) {
      setUploadMessages((currentMessages) => ({
        ...currentMessages,
        [topicName]: 'Upload service is unavailable. Please try again later.',
      }));
    }
  }

  /**
   * Renders the unauthenticated login route.
   *
   * @returns {JSX.Element}
   */
  function renderLoginPage() {
    return (
      <div className="app login-page">
        <h1>Welcome to Project Onion!</h1>
        <Login onLogin={setLoggedInUser} />
      </div>
    );
  }

  /**
   * Renders the main universe page after login.
   *
   * @returns {JSX.Element}
   */
  function renderUniversePage() {
    if (!loggedInUser) {
      return renderLoginPage();
    }

    return (
      <div className="app">
        <section className="page-content">
          <h1>Welcome to Project Onion!</h1>
          <p className="welcome-user">Signed in as {loggedInUser}</p>
          <p>
            We aim to help students draw better connections between difficult concepts.
            To start off, create a topic node and add documents to it.
          </p>
        </section>

        <section className="topic-panel" aria-label="Topics">
          <form className="topic-form" onSubmit={handleCreateTopic}>
            <input
              type="text"
              value={newTopicName}
              onChange={(event) => setNewTopicName(event.target.value)}
              placeholder="Topic name"
              required
            />
            <input
              type="text"
              value={newTopicDescription}
              onChange={(event) => setNewTopicDescription(event.target.value)}
              placeholder="Topic description"
              required
            />
            <button type="submit">Create Topic</button>
          </form>

          {topicMessage && <p className="status-message">{topicMessage}</p>}
        </section>

        {/* Keep the canvas mounted so the universe starts blank instead of appearing late. */}
        <section className="network-panel" aria-label="Concept network preview">
          <NetworkScene
            topics={topics}
            documentsByTopic={documentsByTopic}
            onUploadDocument={handleUploadDocument}
            uploadMessages={uploadMessages}
          />
        </section>
      </div>
    );
  }

  return (
    <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <Routes>
        <Route path="/" element={renderUniversePage()} />
        <Route path="/login" element={renderLoginPage()} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
