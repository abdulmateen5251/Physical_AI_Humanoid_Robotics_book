/**
 * API Client for RAG Chatbot Backend
 * Handles communication with FastAPI backend at /api endpoints
 */

import axios, { AxiosError } from 'axios';

// ====================
// Configuration
// ====================

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout for LLM responses
  headers: {
    'Content-Type': 'application/json',
  },
});

// ====================
// Type Definitions
// ====================

export interface RetrievedChunk {
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

export interface AnswerResponse {
  answer: string;
  sources: RetrievedChunk[];
  metadata: {
    model: string;
    tokens_used?: number;
    retrieval_time_ms: number;
    generation_time_ms: number;
  };
}

export interface FeedbackPayload {
  question: string;
  answer: string;
  feedback_type: 'thumbs_up' | 'thumbs_down';
  comment?: string;
  sources?: string[]; // chunk_ids
}

export interface ErrorResponse {
  detail: string;
  status_code: number;
}

// ====================
// API Functions
// ====================

/**
 * Retrieve relevant chunks from the vector database
 * @param query - User's search query
 * @param topK - Number of chunks to retrieve (default: 5)
 * @param filter - Optional metadata filter (e.g., {"module": "module-01-ros2"})
 * @returns Array of retrieved chunks with scores
 */
export async function retrieveChunks(
  query: string,
  topK: number = 5,
  filter?: Record<string, any>
): Promise<RetrievedChunk[]> {
  try {
    const response = await apiClient.post<RetrievedChunk[]>('/retrieve', {
      query,
      top_k: topK,
      filter,
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Failed to retrieve chunks');
    throw error;
  }
}

/**
 * Get an answer to a question using RAG
 * @param question - User's question
 * @param module - Optional module filter (e.g., "module-01-ros2")
 * @param selectionMode - Whether selection-mode is active (answers based on selected text)
 * @param selectedText - The text selected by user (required if selectionMode=true)
 * @returns Answer with sources and metadata
 */
export async function answerQuestion(
  question: string,
  module?: string,
  selectionMode: boolean = false,
  selectedText?: string
): Promise<AnswerResponse> {
  try {
    const payload: any = {
      question,
      module,
      selection_mode: selectionMode,
    };

    if (selectionMode && selectedText) {
      payload.selected_text = selectedText;
    }

    const response = await apiClient.post<AnswerResponse>('/answer', payload);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Failed to get answer');
    throw error;
  }
}

/**
 * Submit user feedback on an answer
 * @param feedback - Feedback payload with question, answer, and user rating
 * @returns Success status
 */
export async function submitFeedback(feedback: FeedbackPayload): Promise<{ status: string }> {
  try {
    const response = await apiClient.post<{ status: string }>('/feedback', feedback);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Failed to submit feedback');
    throw error;
  }
}

/**
 * Check if the backend is healthy
 * @returns Health status
 */
export async function checkHealth(): Promise<{ status: string; version?: string }> {
  try {
    const response = await apiClient.get<{ status: string; version?: string }>('/health', {
      baseURL: API_BASE_URL.replace('/api', ''), // Health endpoint at root
      timeout: 5000,
    });
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
}

// ====================
// Error Handling
// ====================

function handleApiError(error: unknown, context: string): void {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;
    
    if (axiosError.response) {
      // Server responded with error status
      const status = axiosError.response.status;
      const detail = axiosError.response.data?.detail || axiosError.message;
      console.error(`${context} [${status}]:`, detail);
      
      if (status === 429) {
        console.error('Rate limit exceeded. Please try again later.');
      } else if (status === 500) {
        console.error('Server error. Please contact support if this persists.');
      } else if (status === 422) {
        console.error('Invalid request. Please check your input.');
      }
    } else if (axiosError.request) {
      // Request made but no response
      console.error(`${context}: No response from server. Is the backend running?`);
    } else {
      // Error setting up request
      console.error(`${context}:`, axiosError.message);
    }
  } else {
    console.error(`${context}:`, error);
  }
}

// ====================
// Request/Response Interceptors (optional but useful for debugging)
// ====================

// Log requests in development
if (process.env.NODE_ENV === 'development') {
  apiClient.interceptors.request.use(
    (config) => {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
      return config;
    },
    (error) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  apiClient.interceptors.response.use(
    (response) => {
      console.log(`[API Response] ${response.config.url}`, response.data);
      return response;
    },
    (error) => {
      if (error.response) {
        console.error(
          `[API Response Error] ${error.response.status} ${error.response.config.url}`,
          error.response.data
        );
      }
      return Promise.reject(error);
    }
  );
}

export default {
  retrieveChunks,
  answerQuestion,
  submitFeedback,
  checkHealth,
};
