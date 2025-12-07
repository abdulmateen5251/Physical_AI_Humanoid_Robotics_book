/**
 * ChatContext - State Management for ChatWidget
 * Manages messages, loading state, error handling, and API interactions
 */

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { answerQuestion, submitFeedback } from '../../services/api';
import type { AnswerResponse, FeedbackPayload } from '../../services/api';

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

interface ChatContextType {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string, module?: string) => Promise<void>;
  clearMessages: () => void;
  clearError: () => void;
  sendFeedback: (messageId: string, feedbackType: 'thumbs_up' | 'thumbs_down', comment?: string) => Promise<void>;
}

// ====================
// Context Creation
// ====================

const ChatContext = createContext<ChatContextType | undefined>(undefined);

// ====================
// Provider Component
// ====================

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate unique message ID
  const generateMessageId = (): string => {
    return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  };

  // Send a message and get AI response
  const sendMessage = useCallback(async (content: string, module?: string) => {
    const trimmedContent = content.trim();
    if (!trimmedContent) return;

    // Add user message
    const userMessage: Message = {
      id: generateMessageId(),
      role: 'user',
      content: trimmedContent,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Call API to get answer
      const response: AnswerResponse = await answerQuestion(trimmedContent, module);

      // Add assistant message
      const assistantMessage: Message = {
        id: generateMessageId(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources.map((source) => ({
          chunk_id: source.chunk_id,
          text: source.text,
          metadata: source.metadata,
          score: source.score,
        })),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error getting answer:', err);

      // Add error message
      const errorMessage: Message = {
        id: generateMessageId(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
        timestamp: new Date(),
        isError: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
      setError('Failed to get response. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Clear all messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  // Clear error message
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Send feedback for a message
  const sendFeedback = useCallback(
    async (messageId: string, feedbackType: 'thumbs_up' | 'thumbs_down', comment?: string) => {
      // Find the message and its preceding user message
      const messageIndex = messages.findIndex((msg) => msg.id === messageId);
      if (messageIndex === -1 || messageIndex === 0) {
        console.error('Message not found or no user question found');
        return;
      }

      const assistantMessage = messages[messageIndex];
      const userMessage = messages[messageIndex - 1];

      if (assistantMessage.role !== 'assistant' || userMessage.role !== 'user') {
        console.error('Invalid message pair for feedback');
        return;
      }

      try {
        const feedbackPayload: FeedbackPayload = {
          question: userMessage.content,
          answer: assistantMessage.content,
          feedback_type: feedbackType,
          comment,
          sources: assistantMessage.sources?.map((s) => s.chunk_id),
        };

        await submitFeedback(feedbackPayload);
        console.log('Feedback submitted successfully');

        // Optional: Show a toast notification
        // showToast('Thank you for your feedback!');
      } catch (err) {
        console.error('Error submitting feedback:', err);
        setError('Failed to submit feedback. Please try again.');
      }
    },
    [messages]
  );

  const value: ChatContextType = {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    clearError,
    sendFeedback,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

// ====================
// Custom Hook
// ====================

export const useChatContext = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};

export default ChatContext;
