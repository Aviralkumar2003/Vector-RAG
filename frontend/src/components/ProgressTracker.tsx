import React from 'react';
import './ProgressTracker.css';

interface ProgressTrackerProps {
  stage: string;
  message: string;
  progress: number;
}

const stages = [
  { id: 'loading', label: 'Loading' },
  { id: 'tables', label: 'Tables' },
  { id: 'chunking', label: 'Chunking' },
  { id: 'embedding', label: 'Embedding' },
  { id: 'storing', label: 'Storing' },
  { id: 'complete', label: 'Complete' },
];

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  stage,
  message,
  progress,
}) => {
  const getStageStatus = (stageId: string): 'done' | 'active' | 'pending' => {
    const currentIndex = stages.findIndex((s) => s.id === stage);
    const stageIndex = stages.findIndex((s) => s.id === stageId);

    if (stageIndex < currentIndex) return 'done';
    if (stageIndex === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="progress-tracker-container">
      <div className="progress-bar-wrapper">
        <div className="progress-bar-background">
          <div
            className="progress-bar-fill"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="progress-percentage">{progress}%</div>
      </div>

      <div className="stages-list">
        {stages.map((s, idx) => {
          const status = getStageStatus(s.id);
          return (
            <div key={s.id} className={`stage-item stage-${status}`}>
              <div className="stage-indicator">{status === 'done' ? '✓' : status === 'active' ? '⏳' : '○'}</div>
              <div className="stage-label">{s.label}</div>
              {idx < stages.length - 1 && <div className="stage-connector"></div>}
            </div>
          );
        })}
      </div>

      <div className="progress-message">{message}</div>
    </div>
  );
};
