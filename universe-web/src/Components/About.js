import React from 'react';
import { useNavigate } from 'react-router-dom';
import './About.css';

export default function About() {
  const navigate = useNavigate();

  return (
    <main className="about-page">
      <section className="about-hero" aria-labelledby="about-title">
        <p className="about-wordmark">Project Onion</p>
        <h1 id="about-title" className="about-title">About Us</h1>
        <p className="about-subtitle">
          We help learners turn scattered notes into a visual knowledge universe,
          making concepts easier to organise, explore, and connect.
        </p>
      </section>

      <section className="about-grid" aria-label="Project values">
        <article className="about-card">
          <span className="about-card-icon" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
          </span>
          <h2>Learn Faster</h2>
          <p>
            Upload your materials and let Project Onion extract concepts,
            summaries, and relationships from the content you already have.
          </p>
        </article>

        <article className="about-card">
          <span className="about-card-icon" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20" />
              <path d="M2 12h20" />
              <path d="m4.93 4.93 14.14 14.14" />
              <path d="m19.07 4.93-14.14 14.14" />
            </svg>
          </span>
          <h2>See Connections</h2>
          <p>
            Your concepts become an interactive universe, so you can spot links
            between topics instead of reading notes in isolation.
          </p>
        </article>

        <article className="about-card">
          <span className="about-card-icon" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
              <path d="M8 10h8" />
              <path d="M8 14h5" />
            </svg>
          </span>
          <h2>Ask Your Notes</h2>
          <p>
            The AI assistant answers questions using your uploaded knowledge,
            including references to the concepts it used.
          </p>
        </article>
      </section>

      <section className="about-mission">
        <div>
          <p className="about-section-label">Our Mission</p>
          <h2>Make studying feel navigable.</h2>
        </div>
        <p>
          Project Onion is built around one idea: learning is easier when you can
          see how ideas relate. We combine document processing, semantic search,
          and visual exploration so students can move from raw files to a useful
          mental map.
        </p>
      </section>

    </main>
  );
}
