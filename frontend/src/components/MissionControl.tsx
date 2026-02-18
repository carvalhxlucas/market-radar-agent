import React, { useState } from 'react';

interface MissionData {
  mission_id: string;
  websocket_url: string;
}

interface MissionControlProps {
  onMissionStart: (data: MissionData) => void;
  onMissionStop: () => void;
  isRunning: boolean;
  missionData: MissionData | null;
}

function MissionControl({ onMissionStart, onMissionStop, isRunning, missionData }: MissionControlProps) {
  const [goal, setGoal] = useState<string>('');
  const [headless, setHeadless] = useState<boolean>(true);
  const [maxIterations, setMaxIterations] = useState<number>(50);

  const handleStart = async () => {
    if (!goal.trim()) {
      alert('Por favor, insira um objetivo para a missão.');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/mission/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          goal: goal,
          headless: headless,
          max_iterations: maxIterations,
        }),
      });

      const data: MissionData = await response.json();
      onMissionStart(data);
    } catch (error) {
      console.error('Error starting mission:', error);
      alert('Erro ao iniciar missão. Verifique se o servidor está rodando.');
    }
  };

  const handleStop = async () => {
    if (!missionData?.mission_id) return;

    try {
      await fetch(`http://localhost:8000/mission/${missionData.mission_id}`, {
        method: 'DELETE',
      });
      onMissionStop();
    } catch (error) {
      console.error('Error stopping mission:', error);
    }
  };

  return (
    <div className="card">
      <h2>Controle de Missão</h2>
      
      <label className="label">Objetivo da Missão</label>
      <input
        type="text"
        className="input"
        placeholder="Ex: Encontre o preço médio de Creatina no Brasil"
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        disabled={isRunning}
      />

      <div className="checkbox-group">
        <input
          type="checkbox"
          id="headless"
          checked={headless}
          onChange={(e) => setHeadless(e.target.checked)}
          disabled={isRunning}
        />
        <label htmlFor="headless">Modo headless (sem interface do navegador)</label>
      </div>

      <label className="label">Máximo de Iterações</label>
      <input
        type="number"
        className="input"
        value={maxIterations}
        onChange={(e) => setMaxIterations(parseInt(e.target.value) || 50)}
        min="1"
        max="100"
        disabled={isRunning}
      />

      <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
        {!isRunning ? (
          <button className="button" onClick={handleStart}>
            🚀 Iniciar Missão
          </button>
        ) : (
          <>
            <button className="button button-danger" onClick={handleStop}>
              ⏹️ Parar Missão
            </button>
            <span className="status-badge status-running">Em Execução</span>
          </>
        )}
      </div>

      {missionData && (
        <div style={{ marginTop: '16px', padding: '12px', background: '#f5f5f5', borderRadius: '8px' }}>
          <strong>Mission ID:</strong> {missionData.mission_id.substring(0, 8)}...
        </div>
      )}
    </div>
  );
}

export default MissionControl;
