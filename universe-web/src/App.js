import React, { useCallback, useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';

import './App.css';

import Login from './Login/Login';
import Register from './Login/Register';

import Upload from './Pages/Upload';
import Universe from './Pages/Universe';
import About from './Components/About';

import Sidebar from './Components/Sidebar';
import UserIconButton from './Components/UserIconButton';

import CursorGlow from './Components/CursorGlow';


function App() {
  const [loggedInUser, setLoggedInUser] = useState(localStorage.getItem('username') || '');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Clears all session data and returns the user to login.
  const handleLogout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('tokenExpiresAt');
    localStorage.removeItem('username');
    setLoggedInUser('');
    setSidebarOpen(false);
  }, []);

  // Check whether a valid session already exists or if existing token is expired
  useEffect(() => {
    const token = localStorage.getItem('token');
    const expiresAt = Number(localStorage.getItem('tokenExpiresAt'));
    if (!token || !expiresAt || Date.now() >= expiresAt) {
      handleLogout();
    }
  }, [handleLogout]);

  // Set a timer to log the user out exactly when the token expires.
  useEffect(() => {
    if (!loggedInUser) return;
    const expiresAt = Number(localStorage.getItem('tokenExpiresAt'));
    const msUntilExpiry = expiresAt - Date.now();
    if (msUntilExpiry <= 0) {
      handleLogout();
      return;
    }
    const timer = setTimeout(handleLogout, msUntilExpiry);
    return () => clearTimeout(timer);
  }, [loggedInUser, handleLogout]);

  
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
          />
        </>
      )}
      
      <Routes>
        <Route
          path="/"
          element={loggedInUser
            ? <Upload loggedInUser={loggedInUser} onLogout={handleLogout} />
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

        <Route path="/about" element={ <About /> } />

        <Route path="/register" element={<Register />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
