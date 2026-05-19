import React, { useEffect, useRef } from 'react';
import './MessageList.css';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string;
  status?: string;
  isStreaming?: boolean;
  timestamp?: string;
}

interface MessageListProps {
  messages: Message[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatTimestamp = (ts?: string) => {
    if (!ts) return null;
    try {
      const date = new Date(ts);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return null;
    }
  };

  return (
    <div className="message-list-container">
      {messages.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">💬</div>
          <div className="empty-text">Start a conversation</div>
          <div className="empty-subtext">Ask a question about your PDF</div>
        </div>
      )}

      {messages.map((msg, idx) => (
        <div key={idx} className={`message message-${msg.role}`}>
          <div className="message-header">
            <div className="message-role">{msg.role === 'user' ? 'You' : 'Assistant'}</div>
            {msg.timestamp && <div className="message-time">{formatTimestamp(msg.timestamp)}</div>}
          </div>
          
          {msg.status && !msg.content && (
            <div className="message-status">
              <span className="status-dot"></span>
              {msg.status}
            </div>
          )}
          
          <div className="message-content">
            {msg.content}
            {msg.isStreaming && <span className="streaming-cursor">▌</span>}
          </div>

          {msg.sources && (
            <div className="message-sources">
              <div className="sources-label">Sources:</div>
              <div className="sources-text">{msg.sources}</div>
            </div>
          )}
        </div>
      ))}

      <div ref={messagesEndRef} />
    </div>
  );
};
