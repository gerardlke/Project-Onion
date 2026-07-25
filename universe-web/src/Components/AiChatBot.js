import React, { useEffect, useRef, useState } from 'react';
import { apiFetch } from '../Api';
import './AiChatBot.css';

const INITIAL_MESSAGE = {
  role: 'assistant',
  content: 'Ask me anything about your universe!',
};

export default function AiChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const [serviceAvailable, setServiceAvailable] = useState(true);

  useEffect(() => {
    if (!isOpen) return;
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [isOpen, messages, isSending]);

  async function handleSubmit(event) {
    event.preventDefault();

    const query = input.trim();
    if (!query || isSending) return;

    const previousMessages = messages
      .filter((message) => message !== INITIAL_MESSAGE && !message.isError)
      .map(({ role, content }) => ({ role, content }));
    const userMessage = { role: 'user', content: query };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setInput('');
    setError('');
    setIsSending(true);

    try {
      const response = await apiFetch('/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          conversation_history: previousMessages,
        }),
      });

      if (!response.ok) {
        throw new Error('Chat request failed');
      }

      const result = await response.json();
      const assistantMessage = {
        role: 'assistant',
        content: result.response || 'I could not generate a response.',
        citations: result.citations || [],
        knowledgeGaps: result.knowledge_gaps || [],
        contextFound: result.context_found,
      };

      setMessages((currentMessages) => [...currentMessages, assistantMessage]);
      setServiceAvailable(true);
    } catch {
      setServiceAvailable(false);
      setError('The AI chat service is unavailable right now.');
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: 'assistant',
          content: 'I could not reach the chat service. Please try again.',
          isError: true,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="ai-chatbot" aria-live="polite">
      <button
        className={`ai-chatbot-toggle ${isOpen ? 'ai-chatbot-toggle--open' : ''}`}
        type="button"
        onClick={() => setIsOpen((current) => !current)}
        aria-label={isOpen ? 'Close AI chat' : 'Open AI chat'}
        aria-expanded={isOpen}
      >
        {isOpen ? (
          <span aria-hidden="true">&times;</span>
        ) : (
          <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
            <path d="M8 10h8" />
            <path d="M8 14h5" />
          </svg>
        )}
      </button>

      <section className={`ai-chatbot-panel ${isOpen ? 'ai-chatbot-panel--open' : ''}`} aria-label="AI chat bot">
        <header className="ai-chatbot-header">
          <div>
            <p className="ai-chatbot-eyebrow">Concept Assistant</p>
            <h2>AI-NION</h2>
          </div>
          <span className={`ai-chatbot-status ${
            isSending ? 'ai-chatbot-status--busy' :
            !serviceAvailable ? 'ai-chatbot-status--offline' : ''
          }`}>
            {isSending ? 'Thinking' : !serviceAvailable ? 'Not Available' : 'Online'}
          </span>
        </header>

        <div className="ai-chatbot-messages">
          {messages.map((message, index) => (
            <article
              className={`ai-chatbot-message ai-chatbot-message--${message.role} ${message.isError ? 'ai-chatbot-message--error' : ''}`}
              key={`${message.role}-${index}`}
            >
              <p>{message.content}</p>
              {message.citations?.length > 0 && (
                <div className="ai-chatbot-citations">
                  {message.citations.map((citation, citationIndex) => (
                    <span key={`${citation.concept}-${citationIndex}`}>
                      {citation.concept}
                    </span>
                  ))}
                </div>
              )}
              {message.knowledgeGaps?.length > 0 && (
                <div className="ai-chatbot-gaps">
                  Missing: {message.knowledgeGaps.join(', ')}
                </div>
              )}
            </article>
          ))}

          {isSending && (
            <article className="ai-chatbot-message ai-chatbot-message--assistant">
              <div className="ai-chatbot-typing" aria-label="Assistant is typing">
                <span />
                <span />
                <span />
              </div>
            </article>
          )}
          <div ref={messagesEndRef} />
        </div>

        {error && <p className="ai-chatbot-error">{error}</p>}

        <form className="ai-chatbot-form" onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                handleSubmit(event);
              }
            }}
            placeholder="Type your question..."
            aria-label="Chat message"
            rows={2}
          />
          <button type="submit" disabled={isSending || !input.trim()} aria-label="Send message">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="m22 2-7 20-4-9-9-4Z" />
              <path d="M22 2 11 13" />
            </svg>
          </button>
        </form>
      </section>
    </div>
  );
}
