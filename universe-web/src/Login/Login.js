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

      const user = await response.json();
      onLogin(user.username);
      navigate('/');
    } catch (error) {
      setErrorMessage('Login service is unavailable. Please try again later.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="login-section">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>Login</h2>
        {errorMessage && <p className="errmsg">{errorMessage}</p>}
        <label htmlFor="username">Username</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          required
        />
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Logging in...' : 'Login'}
        </button>
        <p className="register-link">
          Don&apos;t have an account? <Link to="/register">Register here</Link>.
        </p>
      </form>
    </section>
  );
}

export default Login;
