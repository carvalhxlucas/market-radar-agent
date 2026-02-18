import React, { useState, useMemo } from 'react';
import './App.css';
import Chat from './components/Chat';
import SourcesList from './components/SourcesList';
import PriceChart from './components/PriceChart';
import MissionLog from './components/MissionLog';
import { exportToPDF } from './utils/pdfExport';

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

interface ExtractedDataItem {
  prices?: Array<{ value: number; currency: string; raw?: string } | number>;
  product_names?: string[];
  url?: string;
  title?: string;
  average_price?: number;
  currency?: string;
  timestamp?: string;
  [key: string]: any;
}

function App() {
  const [missionData, setMissionData] = useState<MissionData | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [extractedData, setExtractedData] = useState<ExtractedDataItem[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentGoal, setCurrentGoal] = useState<string>('');

  const sources = useMemo(() => {
    return extractedData
      .filter(item => item.url)
      .map(item => ({
        url: item.url!,
        title: item.title,
        timestamp: item.timestamp,
        prices: item.prices?.length || 0
      }));
  }, [extractedData]);

  const handleCommand = async (command: string) => {
    if (!command.trim() || isRunning) return;

    setCurrentGoal(command);
    setLogs([]);
    setExtractedData([]);
    setIsRunning(true);

    try {
      const response = await fetch('http://localhost:8000/mission/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          goal: command,
          headless: true,
          max_iterations: 50,
        }),
      });

      const data: MissionData = await response.json();
      setMissionData(data);
    } catch (error) {
      console.error('Error starting mission:', error);
      alert('Erro ao iniciar missão. Verifique se o servidor está rodando.');
      setIsRunning(false);
    }
  };

  const handleLogUpdate = (log: LogEntry) => {
    setLogs(prev => [...prev, log]);
  };

  const handleDataUpdate = (data: ExtractedDataItem[]) => {
    setExtractedData(data);
  };

  const handleMissionComplete = () => {
    setIsRunning(false);
  };

  const handleExportPDF = async () => {
    if (extractedData.length === 0) {
      alert('Não há dados para exportar.');
      return;
    }

    const summary = logs
      .find(log => log.summary)?.summary || 
      `Total de ${extractedData.length} registros extraídos`;

    await exportToPDF({
      goal: currentGoal || 'Missão MarketRadar',
      data: extractedData,
      sources: sources,
      summary: summary
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <div>
          <h1>MarketRadar</h1>
          <p>Agente Autônomo de Pesquisa de Mercado</p>
        </div>
        <nav className="header-nav">
          <button className="nav-button">Histórico</button>
          {isRunning && (
            <div className="status-indicator">
              <span>Em Execução</span>
            </div>
          )}
          {extractedData.length > 0 && (
            <button
              className="button"
              onClick={handleExportPDF}
              style={{ minWidth: '150px' }}
            >
              Exportar PDF
            </button>
          )}
        </nav>
      </header>
      
      <main className="App-main">
        <div className="main-container">
          <div className="chat-container">
            <Chat
              onSendCommand={handleCommand}
              isRunning={isRunning}
              logs={logs}
            />
          </div>
          
          {(extractedData.length > 0 || sources.length > 0 || logs.length > 0 || isRunning) && (
            <div className="results-container">
              {sources.length > 0 && (
                <SourcesList sources={sources} />
              )}
              
              {extractedData.length > 0 && (
                <PriceChart data={extractedData} />
              )}
              
              {logs.length > 0 && (
                <MissionLog
                  logs={logs}
                  onLogUpdate={handleLogUpdate}
                  onDataUpdate={handleDataUpdate}
                  onMissionComplete={handleMissionComplete}
                  missionData={missionData}
                  isRunning={isRunning}
                />
              )}
              
              {isRunning && extractedData.length === 0 && (
                <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
                  <h2 style={{ color: '#e0e0e0', marginBottom: '10px' }}>Processando...</h2>
                  <p style={{ color: '#b0b0b0' }}>O agente está coletando dados para você</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
