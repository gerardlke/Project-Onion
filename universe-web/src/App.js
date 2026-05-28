
import React, { useState } from 'react';
import './App.css';
import Stars from './Components/Stars';
import NetworkScene from './Components/NetworkScene';
import Login from './Login/Login';

function App() {
  const [loggedInUser, setLoggedInUser] = useState('');
  const [fileUploaded, setFileUploaded] = useState(false);
  const [showPopup, setShowPopup] = useState(false);

  async function fileUploadEvent(event) {
    const file = event.target.files[0];
    if (file) {
      // Handle the file upload logic here
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/upload/', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          setFileUploaded(true);
        } else {
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

  if (!loggedInUser) {
    return (
      <div className="app login-page">
        <h1>Welcome to Project Onion!</h1>
        <Login onLogin={setLoggedInUser} />
      </div>
    );
  }

  return (
      
      <div className="app">
        <h1>Welcome to Project Onion!</h1>
        <p className="welcome-user">Signed in as {loggedInUser}</p>
        <p>We aim to help students draw better connections between difficult concepts.
          To start off, upload your notes or any relevant materials.</p>

      <button type="button" className="upload-button" onClick={handleButtonClick}>
        Upload Your Notes
      </button>
      <div style={{ width: '100vw', height: '100vh', background: '#0b0f19' }}>
      <NetworkScene />
    </div>

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

export default App;
