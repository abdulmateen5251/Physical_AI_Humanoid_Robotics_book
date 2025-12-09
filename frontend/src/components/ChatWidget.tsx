import React, { useState, useEffect } from 'react';

interface SelectionData {
  text: string;
  chapter?: string;
  section?: string;
  page?: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{
    chapter?: string;
    section?: string;
    page?: string;
    uri?: string;
  }>;
}

const ChatWidget: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selection, setSelection] = useState<SelectionData | null>(null);
  const [selectionOnly, setSelectionOnly] = useState(false);
  const [sessionId] = useState(() => {
    // Generate unique session ID
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  });
  const [isVisible, setIsVisible] = useState(true);

  // Capture text selection
  useEffect(() => {
    const handleSelection = () => {
      const selectedText = window.getSelection()?.toString().trim();
      if (selectedText && selectedText.length > 10) {
        // Extract metadata from current page
        const chapterElement = document.querySelector('[data-chapter]');
        const sectionElement = document.querySelector('[data-section]');
        
        setSelection({
          text: selectedText,
          chapter: chapterElement?.getAttribute('data-chapter') || undefined,
          section: sectionElement?.getAttribute('data-section') || undefined,
        });
      } else {
        // Clear selection if nothing is selected
        setSelection(null);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Save input before clearing
    const question = input;
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: question
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    // Save current selection state
    const currentSelection = selection;
    const currentSelectionOnly = selectionOnly;

    try {
      // Only send selection if it has valid text content
      const validSelection = currentSelection?.text ? currentSelection : null;
      const shouldUseSelectionOnly = currentSelectionOnly && !!validSelection;

      console.log('Sending message to backend:', {
        question: question,
        session_id: sessionId,
        selection_only: shouldUseSelectionOnly,
        selection: validSelection
      });

      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          session_id: sessionId,
          selection_only: shouldUseSelectionOnly,
          selection: validSelection
        })
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error:', errorText);
        throw new Error(`Backend returned ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('Received data:', data);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.answer || 'No answer received',
        citations: data.citations || []
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Could not connect to chatbot service. Make sure backend is running on http://localhost:8000'}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {!isVisible && (
        <button style={styles.floatingButton} onClick={() => setIsVisible(true)}>
          💬
        </button>
      )}
      
      {isVisible && (
        <div style={styles.container}>
          <div style={styles.header}>
            <div style={styles.headerTop}>
              <h3 style={styles.title}>Book Q&A Chatbot</h3>
              <div style={styles.headerButtons}>
                <button style={styles.iconButton} onClick={() => setIsVisible(false)} title="Minimize">
                  −
                </button>
              </div>
            </div>
            {selection && (
              <div style={styles.selectionInfo}>
                <label style={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={selectionOnly}
                    onChange={(e) => setSelectionOnly(e.target.checked)}
                  />
                  <span>Answer from selection only</span>
                </label>
                <div style={styles.selectionText}>
                  Selected: "{selection.text.substring(0, 50)}..."
                </div>
              </div>
            )}
          </div>

      <div style={styles.messages}>
        {messages.map((msg, idx) => (
          <div key={idx} style={msg.role === 'user' ? styles.userMessage : styles.assistantMessage}>
            <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong>
            <p>{msg.content}</p>
            {msg.citations && msg.citations.length > 0 && (
              <div style={styles.citations}>
                <strong>Sources:</strong>
                <ul>
                  {msg.citations.map((c, i) => (
                    <li key={i}>
                      {c.chapter && `Chapter: ${c.chapter}`}
                      {c.section && `, Section: ${c.section}`}
                      {c.page && `, Page: ${c.page}`}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && <div style={styles.loading}>Thinking...</div>}
      </div>

      <div style={styles.inputContainer}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask a question about the book..."
          style={styles.input}
        />
        <button onClick={sendMessage} disabled={loading} style={styles.button}>
          Send
        </button>
      </div>
    </div>
      )}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  floatingButton: {
    position: 'fixed',
    bottom: 20,
    right: 20,
    width: 60,
    height: 60,
    borderRadius: '50%',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    fontSize: 24,
    cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
    zIndex: 1000,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  container: {
    position: 'fixed',
    bottom: 20,
    right: 20,
    width: 400,
    maxHeight: 600,
    backgroundColor: '#fff',
    border: '1px solid #ccc',
    borderRadius: 8,
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    display: 'flex',
    flexDirection: 'column',
    zIndex: 1000
  },
  header: {
    padding: 15,
    borderBottom: '1px solid #eee',
    backgroundColor: '#f5f5f5'
  },
  headerTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10
  },
  title: {
    margin: 0,
    fontSize: 16,
    fontWeight: 600
  },
  headerButtons: {
    display: 'flex',
    gap: 5
  },
  iconButton: {
    width: 30,
    height: 30,
    border: 'none',
    backgroundColor: 'transparent',
    color: '#666',
    cursor: 'pointer',
    borderRadius: 4,
    fontSize: 20,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'background-color 0.2s'
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: 5,
    cursor: 'pointer'
  },
  selectionInfo: {
    marginTop: 10,
    fontSize: 12
  },
  selectionText: {
    marginTop: 5,
    fontStyle: 'italic',
    color: '#666'
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: 15,
    maxHeight: 400
  },
  userMessage: {
    marginBottom: 15,
    padding: 10,
    backgroundColor: '#e3f2fd',
    borderRadius: 5
  },
  assistantMessage: {
    marginBottom: 15,
    padding: 10,
    backgroundColor: '#f5f5f5',
    borderRadius: 5
  },
  citations: {
    marginTop: 10,
    fontSize: 11,
    color: '#666',
    borderTop: '1px solid #ddd',
    paddingTop: 8
  },
  loading: {
    textAlign: 'center',
    color: '#999',
    fontStyle: 'italic'
  },
  inputContainer: {
    display: 'flex',
    padding: 15,
    borderTop: '1px solid #eee'
  },
  input: {
    flex: 1,
    padding: 8,
    border: '1px solid #ccc',
    borderRadius: 4,
    marginRight: 8
  },
  button: {
    padding: '8px 16px',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer'
  }
};

export default ChatWidget;
