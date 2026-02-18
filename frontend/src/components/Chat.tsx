import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
}

interface ChatProps {
  onSendCommand: (command: string) => void;
  isRunning: boolean;
  logs: any[];
}

function Chat({ onSendCommand, isRunning, logs }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (logs.length > 0) {
      const lastLog = logs[logs.length - 1];
      if (lastLog.type === 'action' && lastLog.thought) {
        setMessages(prev => {
          const exists = prev.some(m => m.id === `log-${logs.length}`);
          if (!exists) {
            return [...prev, {
              id: `log-${logs.length}`,
              type: 'agent',
              content: `🤔 ${lastLog.thought}\n💭 ${lastLog.reasoning || ''}`,
              timestamp: lastLog.timestamp
            }];
          }
          return prev;
        });
      }
    }
  }, [logs]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isRunning) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    onSendCommand(input);
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  return (
    <div className="card chat-card">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <p className="welcome-text">Olá! Sou o MarketRadar.</p>
            <p className="welcome-subtext">Envie um comando para começar, por exemplo:</p>
            <div className="suggested-actions">
              <div className="action-button" onClick={() => setInput("Encontre o preço médio de Creatina no Brasil")}>
                "Encontre o preço médio de Creatina no Brasil"
              </div>
              <div className="action-button" onClick={() => setInput("Pesquise o preço de Whey Protein no Brasil")}>
                "Pesquise o preço de Whey Protein no Brasil"
              </div>
              <div className="action-button" onClick={() => setInput("Qual o preço médio de suplementos no Brasil?")}>
                "Qual o preço médio de suplementos no Brasil?"
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              style={{
                marginBottom: '16px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: message.type === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              <div
              style={{
                maxWidth: '75%',
                padding: '14px 18px',
                borderRadius: '4px',
                background: message.type === 'user' 
                  ? '#3a3a3a'
                  : '#2a2a2a',
                color: '#e0e0e0',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                border: '1px solid #333',
                marginBottom: '12px'
              }}
              >
                {message.content}
              </div>
              <span
                style={{
                  fontSize: '0.75rem',
                  color: '#999',
                  marginTop: '4px',
                  marginLeft: message.type === 'user' ? '0' : '0',
                  marginRight: message.type === 'user' ? '0' : '0'
                }}
              >
                {message.timestamp}
              </span>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="chat-input-form">
        <div className="chat-input-wrapper">
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder={isRunning ? "Agente está processando..." : "Digite seu comando aqui..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isRunning}
          />
          <button
            type="submit"
            className="chat-send-button"
            disabled={isRunning || !input.trim()}
          >
            {isRunning ? '...' : '→'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default Chat;
