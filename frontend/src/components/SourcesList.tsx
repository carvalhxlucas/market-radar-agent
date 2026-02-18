import React from 'react';

interface Source {
  url: string;
  title?: string;
  timestamp?: string;
  prices?: number;
}

interface SourcesListProps {
  sources: Source[];
}

function SourcesList({ sources }: SourcesListProps) {
  if (sources.length === 0) {
    return (
      <div className="card">
        <h2>Fontes Consultadas</h2>
        <div style={{ color: '#666', textAlign: 'center', padding: '40px' }}>
          <p>Nenhuma fonte consultada ainda.</p>
        </div>
      </div>
    );
  }

  const uniqueSources = Array.from(
    new Map(sources.map(s => [s.url, s])).values()
  );

  return (
    <div className="card">
      <h2>Fontes Consultadas ({uniqueSources.length})</h2>
      
      <div>
        {uniqueSources.map((source, index) => (
          <div
            key={index}
            style={{
              marginBottom: '12px',
              padding: '14px',
              background: '#2a2a2a',
              borderRadius: '4px',
              border: '1px solid #333',
              transition: 'background 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#333';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#2a2a2a';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ flex: 1 }}>
                {source.title && (
                  <div style={{ fontWeight: '600', marginBottom: '4px', color: '#333' }}>
                    {source.title}
                  </div>
                )}
                  <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: '#b0b0b0',
                    textDecoration: 'none',
                    wordBreak: 'break-all',
                    fontSize: '0.9rem',
                    transition: 'color 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.textDecoration = 'underline';
                    e.currentTarget.style.color = '#e0e0e0';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.textDecoration = 'none';
                    e.currentTarget.style.color = '#b0b0b0';
                  }}
                >
                  {source.url}
                </a>
                {source.prices && (
                  <div style={{ marginTop: '8px', fontSize: '0.85rem', color: '#666' }}>
                    {source.prices} preço(s) encontrado(s)
                  </div>
                )}
                {source.timestamp && (
                  <div style={{ marginTop: '4px', fontSize: '0.75rem', color: '#999' }}>
                    {new Date(source.timestamp).toLocaleString()}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SourcesList;
