import React from 'react';

import './Sidebar.css';


export default function Sidebar({ isOpen, onClose, username, onLogout }) {
  return (
    <>
      {isOpen && (
        <div className="sidebar-backdrop" onClick={onClose} aria-hidden="true" />
      )}

      <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`} aria-label="User menu">
        <div className="sidebar-header">
          <div className="sidebar-avatar">
            {username ? username[0].toUpperCase() : '?'}
          </div>
          <div className="sidebar-username">{username}</div>
        </div>

        <div className="sidebar-divider"/>

        <nav className="sidebar-nav">
          <button className="sidebar-signout" onClick={() => { onClose(); onLogout(); }}>
            Sign out
          </button>
        </nav>
      </aside>
    </>
  );
}
