import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MessageList, Message } from '../components/MessageList';
import { ChatInput } from '../components/ChatInput';
import './ChatPage.css';

export const ChatPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pdfFilename, setPdfFilename] = useState<string>('');

  React.useEffect(() => {
    const fetchHistory = async () => {
      if (!sessionId) return;
      
      setIsLoading(true);
      try {
        const response = await fetch(`http://localhost:8000/history/${sessionId}`);
        if (!response.ok) {
          if (response.status === 404) {
            setError('Session not found');
            return;
          }
          throw new Error('Failed to fetch chat history');
        }
        
        const data = await response.json();
        setPdfFilename(data.filename);
        
        // Map DB messages to frontend Message format
        const history: Message[] = data.messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          sources: msg.sources || undefined,
          timestamp: msg.timestamp
        }));
        
        setMessages(history);
      } catch (err) {
        console.error('History fetch error:', err);
        setError('Failed to load chat history');
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, [sessionId]);

  if (!sessionId) {
    return (
      <div className="error-page">
        <div className="error-container">
          <div className="error-icon">✕</div>
          <div className="error-title">Session Not Found</div>
          <p>No session ID provided</p>
          <button className="back-button" onClick={() => navigate('/')}>
            ← Back to Upload
          </button>
        </div>
      </div>
    );
  }

  const handleSend = async (query: string) => {
    if (!query.trim() || isLoading) return;

    setError(null);
    setIsLoading(true);

    // Add user message
    const userMessage: Message = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMessage]);

    // Add initial streaming assistant message
    const initialAssistantMessage: Message = { 
      role: 'assistant', 
      content: '', 
      status: 'Searching PDF...', 
      isStreaming: true 
    };
    setMessages((prev) => [...prev, initialAssistantMessage]);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, session_id: sessionId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 404) {
          setError('Session expired. Please upload a new PDF.');
          setTimeout(() => navigate('/'), 2000);
          return;
        }
        throw new Error(errorData.detail || 'Chat failed');
      }

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = '';
      let accumulatedSources = '';
      let currentStatus = 'Searching PDF...';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.trim().startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.trim().slice(6));

              if (eventData.type === 'status') {
                currentStatus = eventData.content;
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastIdx = newMessages.length - 1;
                  newMessages[lastIdx] = { 
                    ...newMessages[lastIdx], 
                    status: currentStatus 
                  };
                  return newMessages;
                });
              } else if (eventData.type === 'token') {
                accumulatedContent += eventData.content;
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastIdx = newMessages.length - 1;
                  newMessages[lastIdx] = { 
                    ...newMessages[lastIdx], 
                    content: accumulatedContent,
                    status: undefined // Remove status once we start getting content
                  };
                  return newMessages;
                });
              } else if (eventData.type === 'sources') {
                accumulatedSources = eventData.content;
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastIdx = newMessages.length - 1;
                  newMessages[lastIdx] = { 
                    ...newMessages[lastIdx], 
                    sources: accumulatedSources 
                  };
                  return newMessages;
                });
              } else if (eventData.type === 'complete') {
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastIdx = newMessages.length - 1;
                  newMessages[lastIdx] = { 
                    ...newMessages[lastIdx], 
                    isStreaming: false 
                  };
                  return newMessages;
                });
              } else if (eventData.type === 'error') {
                throw new Error(eventData.message || 'Chat error');
              }
            } catch (e) {
              console.error('Parse error:', e, 'Line:', line);
            }
          }
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Chat failed';
      setError(errorMessage);
      
      // Update the last message to show the error if it was streaming
      setMessages((prev) => {
        if (prev.length === 0) return prev;
        const newMessages = [...prev];
        const lastIdx = newMessages.length - 1;
        if (newMessages[lastIdx].role === 'assistant') {
          newMessages[lastIdx] = {
            ...newMessages[lastIdx],
            isStreaming: false,
            content: newMessages[lastIdx].content + `\n\n[Error: ${errorMessage}]`
          };
        }
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-page-container">
      <div className="chat-page-header">
        <div className="header-info">
          <h1>Chat with Your PDF</h1>
          {pdfFilename && <span className="pdf-badge">📄 {pdfFilename}</span>}
        </div>
        <button
          className="new-pdf-button"
          onClick={() => navigate('/')}
          title="Upload a new PDF"
        >
          📄 New PDF
        </button>
      </div>

      <div className="chat-page-content">
        <MessageList messages={messages} />

        {error && <div className="chat-error">{error}</div>}

        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
};
