/**
 * ChatWidget - Main Container Component
 * Collapsible chat interface positioned at bottom-right of screen
 */

import React, { useState, useEffect } from 'react';
import { ChatProvider, useChatContext } from '../context/ChatContext';
import ChatInput from './ChatInput';
import MessageList from './MessageList';
import styles from './styles.module.css';

// ====================
// ChatWidget Component (with Context Provider)
// ====================

const ChatWidget: React.FC = () => {
  return (
    <ChatProvider>
      <ChatWidgetContent />
    </ChatProvider>
  );
};

// ====================
// ChatWidget Content (uses Context)
// ====================

const ChatWidgetContent: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const { messages, sendMessage, isLoading, error, clearError } = useChatContext();

  // Toggle expand/collapse
  const toggleExpand = () => {
    if (isMinimized) {
      setIsMinimized(false);
      setIsExpanded(true);
    } else {
      setIsExpanded(!isExpanded);
    }
  };

  // Minimize (collapse to icon only)
  const handleMinimize = () => {
    setIsMinimized(true);
    setIsExpanded(false);
  };

  // Close chat (hide completely)
  const handleClose = () => {
    setIsExpanded(false);
    setIsMinimized(true);
  };

  // Show unread indicator if new message arrives while minimized
  const [hasUnread, setHasUnread] = useState(false);
  useEffect(() => {
    if (isMinimized && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant') {
        setHasUnread(true);
      }
    } else {
      setHasUnread(false);
    }
  }, [messages, isMinimized]);

  // Handle send message
  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };

  return (
    <div className={styles.chatWidget}>
      {/* Minimized Button (bottom-right corner) */}
      {isMinimized && (
        <button
          className={`${styles.floatingButton} ${hasUnread ? styles.hasUnread : ''}`}
          onClick={toggleExpand}
          aria-label="Open chat"
        >
          <ChatIcon />
          {hasUnread && <span className={styles.unreadBadge} />}
        </button>
      )}

      {/* Expanded Chat Window */}
      {isExpanded && (
        <div className={styles.chatWindow}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.headerTitle}>
              <ChatIcon />
              <h3>AI Learning Assistant</h3>
            </div>
            <div className={styles.headerActions}>
              <button
                className={styles.iconButton}
                onClick={handleMinimize}
                aria-label="Minimize chat"
                title="Minimize"
              >
                <MinimizeIcon />
              </button>
              <button
                className={styles.iconButton}
                onClick={handleClose}
                aria-label="Close chat"
                title="Close"
              >
                <CloseIcon />
              </button>
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div className={styles.errorBanner}>
              <span className={styles.errorText}>{error}</span>
              <button
                className={styles.errorClose}
                onClick={clearError}
                aria-label="Dismiss error"
              >
                ×
              </button>
            </div>
          )}

          {/* Messages */}
          <MessageList messages={messages} isLoading={isLoading} />

          {/* Input */}
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder="Ask a question about the course..."
          />

          {/* Footer */}
          <div className={styles.chatFooter}>
            <span className={styles.footerText}>
              Powered by RAG • <a href="/docs/module-01-ros2/01-introduction">View Docs</a>
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

// ====================
// Icon Components (SVG)
// ====================

const ChatIcon: React.FC = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path
      d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H6L4 18V4H20V16Z"
      fill="currentColor"
    />
    <path d="M7 9H17V11H7V9Z" fill="currentColor" />
    <path d="M7 12H14V14H7V12Z" fill="currentColor" />
  </svg>
);

const MinimizeIcon: React.FC = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path d="M6 19H18V17H6V19Z" fill="currentColor" />
  </svg>
);

const CloseIcon: React.FC = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path
      d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z"
      fill="currentColor"
    />
  </svg>
);

export default ChatWidget;
