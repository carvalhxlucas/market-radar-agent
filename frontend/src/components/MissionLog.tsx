import React, { useEffect, useRef, useState } from 'react';

interface MissionData {
  mission_id: string;
  websocket_url: string;
}

interface LogEntry {
  type: string;
  message?: string;
  timestamp: string;
  iteration?: number;
  thought?: string;
  reasoning?: string;
  action?: {
    name: string;
    params?: Record<string, any>;
  };
  url?: string;
  extractedCount?: number;
  summary?: string;
  totalIterations?: number;
}

interface MissionLogProps {
  logs: LogEntry[];
  onLogUpdate: (log: LogEntry) => void;
  onDataUpdate: (data: any[]) => void;
  onMissionComplete: () => void;
  missionData: MissionData | null;
  isRunning: boolean;
}

function MissionLog({ logs, onLogUpdate, onDataUpdate, onMissionComplete, missionData, isRunning }: MissionLogProps) {
  const logEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<string>('idle');

  useEffect(() => {
    if (!missionData?.mission_id || !isRunning) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/${missionData.mission_id}`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('running');
      onLogUpdate({
        type: 'system',
        message: 'Connected to server',
        timestamp: new Date().toLocaleTimeString(),
      });
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'status') {
        onLogUpdate({
          type: 'status',
          message: data.message,
          url: data.url,
          timestamp: new Date().toLocaleTimeString(),
        });
      } else if (data.type === 'action') {
        onLogUpdate({
          type: 'action',
          iteration: data.iteration,
          thought: data.thought_process,
          reasoning: data.reasoning,
          action: data.action,
          url: data.url,
          extractedCount: data.extracted_data_count,
          timestamp: new Date().toLocaleTimeString(),
        });
      } else if (data.type === 'complete') {
        setStatus('complete');
        onLogUpdate({
          type: 'complete',
          message: 'Mission completed successfully!',
          summary: data.summary,
          totalIterations: data.total_iterations,
          timestamp: new Date().toLocaleTimeString(),
        });
        onDataUpdate(data.extracted_data || []);
        onMissionComplete();
      } else if (data.type === 'incomplete') {
        setStatus('complete');
        onLogUpdate({
          type: 'incomplete',
          message: data.message,
          summary: data.summary,
          timestamp: new Date().toLocaleTimeString(),
        });
        onDataUpdate(data.extracted_data || []);
        onMissionComplete();
      } else if (data.type === 'error') {
        setStatus('error');
        onLogUpdate({
          type: 'error',
          message: data.message,
          timestamp: new Date().toLocaleTimeString(),
        });
        onMissionComplete();
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('error');
        onLogUpdate({
          type: 'error',
          message: 'WebSocket connection error',
          timestamp: new Date().toLocaleTimeString(),
        });
    };

    ws.onclose = () => {
      if (status === 'running') {
        setStatus('idle');
      }
    };

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [missionData, isRunning, status, onLogUpdate, onDataUpdate, onMissionComplete]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLogIcon = (type: string): string => {
    return '';
  };

  const getLogColor = (type: string): string => {
    switch (type) {
      case 'complete':
        return '#555';
      case 'error':
        return '#555';
      case 'action':
        return '#555';
      default:
        return '#444';
    }
  };

  return (
    <div className="card">
      <h2>
        Mission Log
        <span className={`status-badge status-${status}`}>
          {status === 'running' ? 'Running' : 
           status === 'complete' ? 'Complete' : 
           status === 'error' ? 'Error' : 'Waiting'}
        </span>
      </h2>
      
      <div
        style={{
          maxHeight: '500px',
          overflowY: 'auto',
          padding: '16px',
          background: '#2a2a2a',
          borderRadius: '4px',
          fontFamily: 'monospace',
          fontSize: '0.85rem',
          border: '1px solid #333'
        }}
      >
        {          logs.length === 0 ? (
          <div style={{ color: '#666', textAlign: 'center', padding: '40px' }}>
            <p>No logs yet.</p>
            <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>Start a mission to see logs.</p>
          </div>
        ) : (
          logs.map((log, index) => (
            <div
              key={index}
              style={{
                marginBottom: '12px',
                padding: '14px',
                background: '#2a2a2a',
                borderRadius: '4px',
                borderLeft: `4px solid ${getLogColor(log.type)}`,
                border: '1px solid #333',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                <strong style={{ color: '#b0b0b0' }}>
                  {log.type.toUpperCase()}
                </strong>
                <span style={{ marginLeft: 'auto', color: '#999', fontSize: '0.85rem' }}>
                  {log.timestamp}
                </span>
              </div>
              
              {log.message && (
                <div style={{ marginBottom: '4px' }}>{log.message}</div>
              )}
              
              {log.thought && (
                <div style={{ marginTop: '8px', color: '#b0b0b0' }}>
                  <strong>Thought:</strong> {log.thought}
                </div>
              )}
              
              {log.reasoning && (
                <div style={{ marginTop: '4px', color: '#b0b0b0' }}>
                  <strong>Reasoning:</strong> {log.reasoning}
                </div>
              )}
              
              {log.action && (
                <div style={{ marginTop: '8px', padding: '8px', background: '#2a2a2a', borderRadius: '4px', border: '1px solid #333' }}>
                  <strong>Action:</strong> {log.action.name}
                  {log.action.params && (
                    <pre style={{ marginTop: '4px', fontSize: '0.85rem', overflow: 'auto' }}>
                      {JSON.stringify(log.action.params, null, 2)}
                    </pre>
                  )}
                </div>
              )}
              
              {log.url && (
                <div style={{ marginTop: '4px', color: '#b0b0b0', fontSize: '0.85rem' }}>
                  {log.url}
                </div>
              )}
              
              {log.iteration && (
                <div style={{ marginTop: '4px', color: '#666', fontSize: '0.85rem' }}>
                  Iteration #{log.iteration} | Extracted data: {log.extractedCount || 0}
                </div>
              )}
              
              {log.summary && (
                <div style={{ marginTop: '8px', padding: '8px', background: '#2a2a2a', borderRadius: '4px', border: '1px solid #333' }}>
                  <strong>Summary:</strong>
                  <pre style={{ marginTop: '4px', whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
                    {log.summary}
                  </pre>
                </div>
              )}
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}

export default MissionLog;
