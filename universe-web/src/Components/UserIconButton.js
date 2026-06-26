import React from 'react';
import './UserIconButton.css';


export default function UserIconButton({ onClick }) {
  return (
    <button
      className="user-icon-btn"
      onClick={onClick}
      aria-label="Open user menu"
    >
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="8" r="4" />
        <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
      </svg>
    </button>
  );
}
