import React, { useState } from 'react';
import './ChatInput.css';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input-container">
      <div className="chat-input-wrapper">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about your PDF... (Shift+Enter for new line)"
          disabled={disabled}
          className="chat-input-textarea"
          rows={3}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className="chat-input-button"
        >
          {disabled ? '⏳ Waiting...' : '➤ Send'}
        </button>
      </div>
    </div>
  );
};
