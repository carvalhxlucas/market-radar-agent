import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface PriceData {
  value: number;
  currency: string;
  raw?: string;
  timestamp?: string;
  source?: string;
}

interface ExtractedDataItem {
  prices?: (PriceData | number)[];
  url?: string;
  title?: string;
  timestamp?: string;
}

interface PriceChartProps {
  data: ExtractedDataItem[];
}

function PriceChart({ data }: PriceChartProps) {
  const chartData = useMemo(() => {
    const allPrices: Array<{ value: number; timestamp: string; source: string }> = [];

    data.forEach((item, index) => {
      if (item.prices && item.prices.length > 0) {
        item.prices.forEach((price) => {
          const value = typeof price === 'object' ? price.value : price;
          const timestamp = item.timestamp || new Date().toISOString();
          const source = item.title || item.url || `Source ${index + 1}`;
          
          allPrices.push({
            value,
            timestamp: new Date(timestamp).toLocaleString('pt-BR', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            }),
            source: source.substring(0, 30)
          });
        });
      }
    });

    return allPrices.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  }, [data]);

  const averagePrice = useMemo(() => {
    if (chartData.length === 0) return null;
    const sum = chartData.reduce((acc, item) => acc + item.value, 0);
    return sum / chartData.length;
  }, [chartData]);

  if (chartData.length === 0) {
    return null;
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2>Price History</h2>
        {averagePrice && (
          <div style={{
            padding: '8px 16px',
            background: '#3a3a3a',
            color: '#e0e0e0',
            borderRadius: '4px',
            fontSize: '0.9rem',
            fontWeight: '500',
            border: '1px solid #444'
          }}>
            Average: R$ {averagePrice.toFixed(2).replace('.', ',')}
          </div>
        )}
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis 
            dataKey="timestamp" 
            stroke="#666"
            fontSize={11}
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fill: '#999' }}
          />
          <YAxis 
            stroke="#666"
            fontSize={11}
            tick={{ fill: '#999' }}
            tickFormatter={(value) => `R$ ${value.toFixed(2)}`}
          />
          <Tooltip
            formatter={(value: number) => [`R$ ${value.toFixed(2).replace('.', ',')}`, 'Price']}
            labelStyle={{ color: '#e0e0e0' }}
            contentStyle={{
              background: '#252525',
              border: '1px solid #333',
              borderRadius: '4px',
              padding: '12px',
              color: '#e0e0e0'
            }}
          />
          <Legend 
            wrapperStyle={{ color: '#b0b0b0' }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#666"
            strokeWidth={2}
            dot={{ fill: '#888', r: 4, strokeWidth: 1, stroke: '#666' }}
            activeDot={{ r: 6, fill: '#999' }}
            name="Price (R$)"
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div style={{ marginTop: '16px', fontSize: '0.85rem', color: '#b0b0b0' }}>
        Total data points: {chartData.length}
      </div>
    </div>
  );
}

export default PriceChart;
