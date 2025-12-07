/**
 * ChatInput Component
 * Text input with send button and loading state
 */

import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import styles from './styles.module.css';

// ====================
// Props Interface
// ====================

interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

// ====================
// ChatInput Component
// ====================

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = 'Type your question...',
  maxLength = 500,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setInputValue(value);
    }
  };

  // Handle send
  const handleSend = async () => {
    const trimmedValue = inputValue.trim();
    
    if (!trimmedValue || isSending || disabled) {
      return;
    }

    setIsSending(true);
    try {
      await onSendMessage(trimmedValue);
      setInputValue(''); // Clear input on success
    } catch (error) {
      console.error('Failed to send message:', error);
      // Keep input value so user can retry
    } finally {
      setIsSending(false);
      // Focus textarea after sending
      textareaRef.current?.focus();
    }
  };

  // Handle Enter key (send message, Shift+Enter for new line)
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Character counter
  const remainingChars = maxLength - inputValue.length;
  const showCharCounter = inputValue.length > maxLength * 0.8;

  return (
    <div className={styles.chatInputContainer}>
      {/* Character Counter */}
      {showCharCounter && (
        <div className={styles.charCounter}>
          {remainingChars} characters remaining
        </div>
      )}

      {/* Input Area */}
      <div className={styles.inputWrapper}>
        <textarea
          ref={textareaRef}
          className={styles.textarea}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isSending}
          rows={1}
          aria-label="Chat input"
          aria-describedby="chat-input-help"
        />

        {/* Send Button */}
        <button
          className={`${styles.sendButton} ${
            inputValue.trim() && !disabled && !isSending ? styles.sendButtonActive : ''
          }`}
          onClick={handleSend}
          disabled={!inputValue.trim() || disabled || isSending}
          aria-label="Send message"
        >
          {isSending ? <LoadingIcon /> : <SendIcon />}
        </button>
      </div>

      {/* Help Text */}
      <div id="chat-input-help" className={styles.helpText}>
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
};

// ====================
// Icon Components
// ====================

const SendIcon: React.FC = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path
      d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z"
      fill="currentColor"
    />
  </svg>
);

const LoadingIcon: React.FC = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    className={styles.loadingSpinner}
  >
    <circle
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      fill="none"
      strokeDasharray="50 50"
    />
  </svg>
);

export default ChatInput;
