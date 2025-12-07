/**
 * ChatWidget Component
 * Provides RAG Q&A interface integrated with the backend API
 */

import React, { useState, useRef, useEffect } from 'react';
import { useAnswer, useHealthCheck } from '../../utils/useApi';
import styles from './ChatWidget.module.css';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hi! 👋 I can help you learn ROS 2. Ask me anything about the course content.',
    },
  ]);
  const [input, setInput] = useState('');
  const { answer, loading, error } = useAnswer();
  const { healthy, error: healthError, check: checkHealth } = useHealthCheck();
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Check backend health on mount
  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when widget opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;
    if (!healthy) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'error',
        content: '❌ Backend is not available. Please check if the API is running.',
      }]);
      return;
    }

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      // Get AI answer
      const result = await answer(input);
      
      // Add assistant message with citations
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: result.answer,
        citations: result.citations || [],
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `❌ ${err.message || 'Failed to get answer. Please try again.'}`,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Chat Button */}
      <button
        className={styles.chatButton}
        onClick={() => setIsOpen(!isOpen)}
        title={healthy ? 'Ask AI' : 'Backend unavailable'}
        style={{ opacity: healthy ? 1 : 0.5 }}
      >
        💬
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className={styles.chatWindow}>
          {/* Header */}
          <div className={styles.header}>
            <h3>
              AI Tutor {healthy ? '✅' : '⚠️'}
            </h3>
            <button
              className={styles.closeButton}
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div className={styles.messages}>
            {messages.map(msg => (
              <div key={msg.id} className={`${styles.message} ${styles[msg.type]}`}>
                <div className={styles.messageContent}>
                  <p>{msg.content}</p>
                  {msg.citations && msg.citations.length > 0 && (
                    <div className={styles.citations}>
                      <strong>Sources:</strong>
                      <ul>
                        {msg.citations.map((citation, idx) => (
                          <li key={idx}>
                            <a
                              href={citation.url || '#'}
                              target="_blank"
                              rel="noopener noreferrer"
                              className={styles.citationLink}
                            >
                              {citation.title || citation.document || `Source ${idx + 1}`}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className={`${styles.message} ${styles.assistant}`}>
                <div className={styles.messageContent}>
                  <p className={styles.typing}>
                    <span></span><span></span><span></span>
                  </p>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className={styles.inputContainer}>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question..."
              disabled={loading || !healthy}
              className={styles.input}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim() || !healthy}
              className={styles.sendButton}
            >
              {loading ? '...' : '→'}
            </button>
          </div>

          {/* Status */}
          {!healthy && (
            <div className={styles.status}>
              ⚠️ Backend unavailable - restart with: `docker compose up`
            </div>
          )}
        </div>
      )}
    </>
  );
}
