import React, { useRef, useState } from 'react';
import './FileDropzone.css';

interface FileDropzoneProps {
  onFileSelected: (file: File) => void;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({ onFileSelected }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      setError('Please upload a PDF file');
      return false;
    }
    setError(null);
    return true;
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelected(file);
      }
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelected(file);
      }
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-dropzone-container">
      <div
        className={`file-dropzone ${isDragging ? 'dragging' : ''} ${selectedFile ? 'selected' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />

        {selectedFile ? (
          <div className="file-selected">
            <div className="file-icon">📄</div>
            <div className="file-name">{selectedFile.name}</div>
            <div className="file-size">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </div>
          </div>
        ) : (
          <div className="file-prompt">
            <div className="drop-icon">⬇️</div>
            <div className="drop-text">Drag and drop your PDF here</div>
            <div className="or-text">or click to select</div>
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};
