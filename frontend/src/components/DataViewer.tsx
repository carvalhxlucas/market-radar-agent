import React from 'react';

interface PriceData {
  value: number;
  currency: string;
  raw?: string;
}

interface ExtractedDataItem {
  prices?: (PriceData | number)[];
  product_names?: string[];
  url?: string;
  title?: string;
  average_price?: number;
  currency?: string;
  timestamp?: string;
  [key: string]: any;
}

interface DataViewerProps {
  data: ExtractedDataItem[];
}

function DataViewer({ data }: DataViewerProps) {
  if (!data || data.length === 0) {
    return (
      <div className="card">
        <h2>Extracted Data</h2>
        <div style={{ color: '#999', textAlign: 'center', padding: '20px' }}>
          No data extracted yet.
        </div>
      </div>
    );
  }

  const formatPrice = (value: number, currency: string = 'BRL'): string => {
    if (currency === 'BRL') {
      return `R$ ${value.toFixed(2).replace('.', ',')}`;
    }
    return `${currency} ${value.toFixed(2)}`;
  };

  const calculateAverage = (prices: (PriceData | number)[] | undefined): number | null => {
    if (!prices || prices.length === 0) return null;
    const values = prices
      .map(p => typeof p === 'object' ? p.value : p)
      .filter((v): v is number => typeof v === 'number');
    if (values.length === 0) return null;
    return values.reduce((a, b) => a + b, 0) / values.length;
  };

  return (
    <div className="card">
      <h2>Extracted Data ({data.length} records)</h2>
      
      <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
        {data.map((item, index) => {
          const prices = item.prices || [];
          const avgPrice = calculateAverage(prices);
          
          return (
            <div
              key={index}
              style={{
                marginBottom: '16px',
                padding: '16px',
                background: '#2a2a2a',
                borderRadius: '4px',
                border: '1px solid #333',
              }}
            >
              <h3 style={{ marginBottom: '12px', color: '#e0e0e0' }}>
                Record #{index + 1}
              </h3>
              
              {item.title && (
                <div style={{ marginBottom: '8px' }}>
                  <strong>Title:</strong> {item.title}
                </div>
              )}
              
              {item.url && (
                <div style={{ marginBottom: '8px' }}>
                  <strong>URL:</strong>{' '}
                  <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ color: '#b0b0b0' }}>
                    {item.url}
                  </a>
                </div>
              )}
              
              {prices.length > 0 && (
                <div style={{ marginBottom: '12px' }}>
                  <strong>Prices found ({prices.length}):</strong>
                  <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {prices.map((price, pIndex) => (
                      <span
                        key={pIndex}
                        style={{
                          padding: '6px 12px',
                          background: '#3a3a3a',
                          color: '#e0e0e0',
                          borderRadius: '4px',
                          fontSize: '0.9rem',
                          fontWeight: '500',
                          border: '1px solid #444',
                        }}
                      >
                        {typeof price === 'object' 
                          ? formatPrice(price.value, price.currency) 
                          : formatPrice(price)}
                      </span>
                    ))}
                  </div>
                  {avgPrice !== null && (
                    <div style={{ marginTop: '12px', padding: '12px', background: '#2a2a2a', borderRadius: '4px', border: '1px solid #333' }}>
                      <strong>Average Price:</strong>{' '}
                      <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#e0e0e0' }}>
                        {formatPrice(avgPrice)}
                      </span>
                    </div>
                  )}
                </div>
              )}
              
              {item.average_price && (
                <div style={{ marginTop: '12px', padding: '12px', background: '#2a2a2a', borderRadius: '4px', border: '1px solid #333' }}>
                  <strong>Calculated Average:</strong>{' '}
                  <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#e0e0e0' }}>
                    {formatPrice(item.average_price, item.currency || 'BRL')}
                  </span>
                </div>
              )}
              
              {item.product_names && item.product_names.length > 0 && (
                <div style={{ marginTop: '12px' }}>
                  <strong>Products found:</strong>
                  <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                    {item.product_names.slice(0, 10).map((product, pIndex) => (
                      <li key={pIndex} style={{ marginBottom: '4px' }}>{product}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {item.timestamp && (
                <div style={{ marginTop: '8px', fontSize: '0.85rem', color: '#999' }}>
                  Extracted at: {new Date(item.timestamp).toLocaleString()}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default DataViewer;
