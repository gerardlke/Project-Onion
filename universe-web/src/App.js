import React, { useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import Stars from './Components/Stars';
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
  const [uploadedFile, setUploadedFile] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const fileUploaded = Boolean(uploadedFile);

  /**
   * Handles file selection from the upload dialog.
   *
   * The selected file is stored immediately so the universe can create a node
   * without waiting for backend processing. The upload request still runs in the
   * background so the server can process the document when it is available.
   *
   * @param {React.ChangeEvent<HTMLInputElement>} event - File input change event.
   * @returns {Promise<void>}
   */
  async function fileUploadEvent(event) {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
      setShowPopup(false);

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/upload/', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          console.error('File upload failed');
        }
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
  }

  function handleButtonClick() {
    setShowPopup(true);
  }

  function closePopup() {
    setShowPopup(false);
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
            To start off, upload your notes or any relevant materials.
          </p>

          <button type="button" className="upload-button" onClick={handleButtonClick}>
            Upload Your Notes
          </button>
        </section>

        {/* Keep the canvas mounted so the universe starts blank instead of appearing late. */}
        <section className="network-panel" aria-label="Concept network preview">
          <NetworkScene uploadedFile={uploadedFile} />
        </section>

        {showPopup && (
          <div className="popup-overlay" role="presentation">
            <section className="popup" role="dialog" aria-modal="true" aria-labelledby="upload-title">
              <button type="button" className="popup-close" onClick={closePopup} aria-label="Close">
                &times;
              </button>
              <h2 id="upload-title">Upload Your Notes</h2>
              <p>Select a document to add to your universe.</p>
              <label htmlFor="file-upload" className="upload-button popup-upload-button">
                Choose File
              </label>
              <input
                type="file"
                id="file-upload"
                onChange={fileUploadEvent}
                className="file-input"
              />
            </section>
          </div>
        )}
        {fileUploaded && <p>File uploaded successfully!</p>}
        {fileUploaded && <Stars />}
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
