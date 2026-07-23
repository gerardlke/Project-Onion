import React, { useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';

import './App.css';

import Login from './Login/Login';
import Register from './Login/Register';

import Upload from './Pages/Upload';
import Universe from './Pages/Universe';

import Sidebar from './Components/Sidebar';
import UserIconButton from './Components/UserIconButton';
import AiChatBot from './Components/AiChatBot';

import CursorGlow from './Components/CursorGlow';

/**
 * Root application component.
 *
 * Responsibilities:
 * - Hold top-level UI state for login, upload modal visibility, and the latest uploaded file.
 * - Render login/register routes before a user is signed in.
 * - Keep the network canvas mounted after login so the universe is visible before and after upload.
 */
function App() {
  const [loggedInUser, setLoggedInUser] = useState(localStorage.getItem('username') || '');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarTopics, setSidebarTopics] = useState([]);

  // Clears all session data and returns the user to login.
  function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('tokenExpiresAt');
    setLoggedInUser('');
    setSidebarOpen(false);
  }

  // Check whether a valid session already exists or if existing token is expired
  useEffect(() => {
    const token = localStorage.getItem('token');
    const expiresAt = Number(localStorage.getItem('tokenExpiresAt'));
    if (!token || !expiresAt || Date.now() >= expiresAt) {
      handleLogout();
    }
  }, []);

  // Set a timer to log the user out exactly when the token expires.
  useEffect(() => {
    if (!loggedInUser) return;

    const expiresAt = Number(localStorage.getItem('tokenExpiresAt'));
    const msUntilExpiry = expiresAt - Date.now();

    if (msUntilExpiry <= 0) {
      handleLogout();
      return;
    }

    const timer = setTimeout(() => {
      handleLogout();
    }, msUntilExpiry);

    return () => clearTimeout(timer);   // clean up if user logs out manually first
  }, [loggedInUser]);

  
  return (
    <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <CursorGlow size={200} />

      {loggedInUser && (
        <>
          <UserIconButton onClick={() => setSidebarOpen(true)} />
          <Sidebar
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            username={loggedInUser}
            onLogout={handleLogout}
            topics={sidebarTopics}
          />
        </>
      )}
      
      <Routes>
        <Route
          path="/"
          element={loggedInUser
            ? <Upload loggedInUser={loggedInUser} onLogout={handleLogout} onTopicsChange={setSidebarTopics} />
            : <Navigate to="/login" replace />}
        />

        <Route
          path="/universe"
          element={loggedInUser
            ? <Universe onLogout={handleLogout} />
            : <Navigate to="/login" replace />}
        />
        
        <Route
          path="/login"
          element={loggedInUser ? <Navigate to="/" replace /> : (
            <Login onLogin={setLoggedInUser} />
          )}
        />

        <Route path="/register" element={<Register />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
