import React, { useState } from 'react';
import './Login.css';
import { Link, useNavigate } from 'react-router-dom';

function Login({ onLogin }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setErrorMessage('');
    setIsSubmitting(true);

    try {
      const response = await fetch('/user/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        setErrorMessage(errorBody?.detail || 'Login failed. Please try again.');
        return;
      }
      
      // Parse json from API response
      const user = await response.json();

      // Set global variables required later
      const expiresAt = Date.now() + 60 * 60 * 1000; // 1 hour from now in ms
      localStorage.setItem('tokenExpiresAt', String(expiresAt));
      localStorage.setItem('token', user.access_token);
      localStorage.setItem('username', username);
      
      // Confirm log in and navigate to universe page
      onLogin(user.username);
      navigate('/');
    } catch (error) {
      setErrorMessage('Login service is unavailable. Please try again later.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <p className="auth-wordmark">Project Onion</p>
      <div className="auth-card">
        <div className="auth-card-header">
          <p className="auth-card-eyebrow">Welcome back</p>
          <h2 className="auth-card-title">Sign in</h2>
        </div>

        {errorMessage && <p className="auth-error">{errorMessage}</p>}

        <form onSubmit={handleSubmit}>
          <div className="auth-field">
            <label className="auth-label" htmlFor="username">Username</label>
            <input
              id="username"
              className="auth-input"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="your username"
              required
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="password">Password</label>
            <input
              id="password"
              className="auth-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button className="auth-btn" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="auth-footer">
          No account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
