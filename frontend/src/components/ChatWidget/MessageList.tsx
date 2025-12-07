/**
 * MessageList Component
 * Displays chat messages with user/assistant distinction, timestamps, and source citations
 */

import React, { useEffect, useRef } from 'react';
import styles from './styles.module.css';

// ====================
// Type Definitions
// ====================

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  isError?: boolean;
}

export interface Source {
  chunk_id: string;
  text: string;
  metadata: {
    source: string;
    page?: number;
    module?: string;
    chapter?: string;
  };
  score: number;
}

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

// ====================
// MessageList Component
// ====================

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading = false }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className={styles.messageList}>
      {/* Empty State */}
      {messages.length === 0 && !isLoading && (
        <div className={styles.emptyState}>
          <WelcomeIcon />
          <h4>Welcome to the AI Learning Assistant!</h4>
          <p>Ask me anything about the course content:</p>
          <ul className={styles.suggestionList}>
            <li>• What is ROS 2 and how is it different from ROS 1?</li>
            <li>• How do I create a publisher node?</li>
            <li>• Explain QoS settings in ROS 2</li>
            <li>• What are the best practices for URDF modeling?</li>
          </ul>
        </div>
      )}

      {/* Messages */}
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {/* Loading Indicator */}
      {isLoading && (
        <div className={`${styles.messageBubble} ${styles.assistantMessage}`}>
          <div className={styles.messageContent}>
            <div className={styles.typingIndicator}>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
            </div>
          </div>
        </div>
      )}

      {/* Scroll Anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
};

// ====================
// MessageBubble Component
// ====================

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';
  const isError = message.isError;

  return (
    <div
      className={`${styles.messageBubble} ${
        isUser ? styles.userMessage : styles.assistantMessage
      } ${isError ? styles.errorMessage : ''}`}
    >
      {/* Avatar */}
      <div className={styles.messageAvatar}>
        {isUser ? <UserIcon /> : <BotIcon />}
      </div>

      {/* Content */}
      <div className={styles.messageContent}>
        {/* Text */}
        <div className={styles.messageText}>
          {isError ? (
            <>
              <strong>Error:</strong> {message.content}
            </>
          ) : (
            formatMessageContent(message.content)
          )}
        </div>

        {/* Sources (only for assistant messages) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceCitations sources={message.sources} />
        )}

        {/* Timestamp */}
        <div className={styles.messageTimestamp}>
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

// ====================
// SourceCitations Component
// ====================

const SourceCitations: React.FC<{ sources: Source[] }> = ({ sources }) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  return (
    <div className={styles.sourceCitations}>
      <button
        className={styles.sourcesToggle}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <SourceIcon />
        <span>Sources ({sources.length})</span>
        <ChevronIcon isExpanded={isExpanded} />
      </button>

      {isExpanded && (
        <div className={styles.sourcesList}>
          {sources.map((source, index) => (
            <div key={source.chunk_id} className={styles.sourceItem}>
              <div className={styles.sourceHeader}>
                <span className={styles.sourceNumber}>{index + 1}</span>
                <span className={styles.sourceTitle}>
                  {source.metadata.module || 'Unknown Module'}
                  {source.metadata.chapter && ` - ${source.metadata.chapter}`}
                </span>
                <span className={styles.sourceScore}>
                  {Math.round(source.score * 100)}% match
                </span>
              </div>
              <div className={styles.sourceText}>
                "{source.text.substring(0, 150)}
                {source.text.length > 150 ? '...' : ''}"
              </div>
              {source.metadata.source && (
                <a
                  href={`/docs/${source.metadata.source}`}
                  className={styles.sourceLink}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View full chapter →
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ====================
// Utility Functions
// ====================

function formatMessageContent(content: string): React.ReactNode {
  // Convert markdown-style code blocks to <code>
  const codeBlockRegex = /```([\s\S]*?)```/g;
  const inlineCodeRegex = /`([^`]+)`/g;

  let formatted = content;

  // Replace code blocks
  formatted = formatted.replace(codeBlockRegex, (match, code) => {
    return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
  });

  // Replace inline code
  formatted = formatted.replace(inlineCodeRegex, (match, code) => {
    return `<code>${escapeHtml(code)}</code>`;
  });

  return <div dangerouslySetInnerHTML={{ __html: formatted }} />;
}

function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatTimestamp(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins === 1) return '1 minute ago';
  if (diffMins < 60) return `${diffMins} minutes ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours === 1) return '1 hour ago';
  if (diffHours < 24) return `${diffHours} hours ago`;

  // Show time for older messages
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ====================
// Icon Components
// ====================

const WelcomeIcon: React.FC = () => (
  <svg
    width="64"
    height="64"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={styles.welcomeIcon}
  >
    <path
      d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z"
      fill="currentColor"
    />
  </svg>
);

const UserIcon: React.FC = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z"
      fill="currentColor"
    />
  </svg>
);

const BotIcon: React.FC = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M20 9V7C20 5.89 19.1 5 18 5H13V2.5C13 1.67 12.33 1 11.5 1C10.67 1 10 1.67 10 2.5V5H6C4.9 5 4 5.89 4 7V9C2.9 9 2 9.9 2 11V13C2 14.1 2.9 15 4 15V19C4 20.1 4.9 21 6 21H18C19.1 21 20 20.1 20 19V15C21.1 15 22 14.1 22 13V11C22 9.9 21.1 9 20 9ZM18 19H6V7H18V19ZM9 13C9 13.55 8.55 14 8 14C7.45 14 7 13.55 7 13C7 12.45 7.45 12 8 12C8.55 12 9 12.45 9 13ZM17 13C17 13.55 16.55 14 16 14C15.45 14 15 13.55 15 13C15 12.45 15.45 12 16 12C16.55 12 17 12.45 17 13ZM8 16H16V17H8V16Z"
      fill="currentColor"
    />
  </svg>
);

const SourceIcon: React.FC = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V8L14 2ZM16 18H8V16H16V18ZM16 14H8V12H16V14ZM13 9V3.5L18.5 9H13Z"
      fill="currentColor"
    />
  </svg>
);

const ChevronIcon: React.FC<{ isExpanded: boolean }> = ({ isExpanded }) => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
  >
    <path d="M7 10L12 15L17 10H7Z" fill="currentColor" />
  </svg>
);

export default MessageList;
