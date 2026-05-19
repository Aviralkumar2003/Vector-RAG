import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileDropzone } from '../components/FileDropzone';
import { ProgressTracker } from '../components/ProgressTracker';
import './UploadPage.css';

type ProcessingStage = 'loading' | 'tables' | 'chunking' | 'embedding' | 'storing' | 'complete';

interface ProcessEvent {
  type: string;
  stage?: ProcessingStage;
  message?: string;
  progress?: number;
}

interface Session {
  id: string;
  filename: string;
  status: string;
  created_at: string;
}

export const UploadPage: React.FC = () => {
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [stage, setStage] = useState<ProcessingStage>('loading');
  const [message, setMessage] = useState('');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);

  React.useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data);
      }
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this chat?')) return;

    try {
      const response = await fetch(`http://localhost:8000/sessions/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setSessions((prev) => prev.filter((s) => s.id !== id));
      } else {
        const data = await response.json();
        alert(data.detail || 'Failed to delete session');
      }
    } catch (err) {
      console.error('Delete error:', err);
      alert('Failed to delete session');
    }
  };

  const handleFileSelected = async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      // POST /upload
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const uploadData = await uploadResponse.json();
      const newSessionId = uploadData.session_id;
      setSessionId(newSessionId);
      setIsUploading(false);

      // Start processing with EventSource
      await startProcessing(newSessionId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setIsUploading(false);
    }
  };

  const startProcessing = async (id: string) => {
    setIsProcessing(true);
    setProgress(0);
    setStage('loading');
    setMessage('Starting ingestion...');

    try {
      const eventSource = new EventSource(`http://localhost:8000/process/${id}`);

      eventSource.addEventListener('message', (event) => {
        const data: ProcessEvent = JSON.parse(event.data);

        if (data.type === 'stage') {
          setStage(data.stage!);
          setMessage(data.message || '');
          setProgress(data.progress || 0);
        } else if (data.type === 'complete') {
          setProgress(100);
          setStage('complete');
          setMessage(data.message || 'Ready to chat!');
          eventSource.close();
          setIsProcessing(false);
        } else if (data.type === 'error') {
          setError(data.message || 'Processing failed');
          eventSource.close();
          setIsProcessing(false);
        }
      });

      eventSource.addEventListener('error', (err) => {
        console.error('EventSource error:', err);
        setError('Connection lost during processing');
        eventSource.close();
        setIsProcessing(false);
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed');
      setIsProcessing(false);
    }
  };

  const handleStartChatting = () => {
    if (sessionId && stage === 'complete') {
      navigate(`/chat/${sessionId}`);
    }
  };

  const handleReset = () => {
    setSessionId(null);
    setIsUploading(false);
    setIsProcessing(false);
    setStage('loading');
    setMessage('');
    setProgress(0);
    setError(null);
  };

  return (
    <div className="upload-page-container">
      <div className="upload-page-header">
        <h1>AskMyPdf</h1>
        <p>Upload a PDF and chat with it using AI</p>
      </div>

      <div className="upload-page-content">
        {!isProcessing && !isUploading && stage !== 'complete' && (
          <FileDropzone onFileSelected={handleFileSelected} />
        )}

        {(isProcessing || isUploading) && (
          <ProgressTracker stage={stage} message={message} progress={progress} />
        )}

        {stage === 'complete' && !error && (
          <div className="completion-state">
            <div className="completion-icon">✓</div>
            <div className="completion-title">PDF Ready!</div>
            <div className="completion-text">Your PDF has been processed and is ready for chat</div>
            <button className="start-chatting-button" onClick={handleStartChatting}>
              Start Chatting →
            </button>
          </div>
        )}

        {error && (
          <div className="error-state">
            <div className="error-icon">✕</div>
            <div className="error-title">Something went wrong</div>
            <div className="error-text">{error}</div>
            <button className="retry-button" onClick={handleReset}>
              Try Again
            </button>
          </div>
        )}

        {!isProcessing && !isUploading && sessions.length > 0 && (
          <div className="previous-sessions">
            <h2>Previous Chats</h2>
            <div className="sessions-list">
              {sessions.map((session) => (
                <div 
                  key={session.id} 
                  className="session-item"
                  onClick={() => navigate(`/chat/${session.id}`)}
                >
                  <div className="session-info">
                    <span className="session-filename">📄 {session.filename}</span>
                    <span className="session-date">
                      {new Date(session.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="session-status">
                    <span className={`status-badge ${session.status}`}>
                      {session.status}
                    </span>
                    <button 
                      className="delete-session-button"
                      onClick={(e) => handleDeleteSession(e, session.id)}
                      title="Delete chat"
                    >
                      🗑️
                    </button>
                    <span className="arrow">→</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

