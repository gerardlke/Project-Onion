import React from 'react';

import './Sidebar.css';
import { TOPIC_COLORS } from '../Data/network.js';


export default function Sidebar({ isOpen, onClose, username, onLogout, topics = [] }) {
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

        <div className="sidebar-divider" />

        {topics.length > 0 && (
          <div className="sidebar-topics">
            <p className="sidebar-topics-label">Topics</p>
            <ul className="sidebar-topics-list">
              {topics.map((topic, index) => (
                <li key={topic.name} className="sidebar-topic-item">
                  <span
                    className="sidebar-topic-dot"
                    style={{ background: TOPIC_COLORS[index % TOPIC_COLORS.length] }}
                  />
                  <span className="sidebar-topic-name">{topic.name}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <nav className="sidebar-nav">
          <button className="sidebar-signout" onClick={() => { onClose(); onLogout(); }}>
            Sign out
          </button>
        </nav>
      </aside>
    </>
  );
}
