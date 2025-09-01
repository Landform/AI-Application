// src/components/ProductivityInfographic.tsx (Corrected for Test Data)
import { useState, useEffect } from 'react';
import { fetchOvertimeData, fetchFocusHeatmapData } from '../api';
import type { OvertimeDataPoint, HeatmapDataPoint } from '../api/types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const getHeatmapColor = (score: number) => {
  if (score > 0.7) return '#28a745'; // Green
  if (score > 0.4) return '#ffc107'; // Yellow
  return '#dc3545'; // Red
};

const ProductivityInfographic = () => {
  const [overtimeData, setOvertimeData] = useState<OvertimeDataPoint[]>([]);
  const [heatmapData, setHeatmapData] = useState<HeatmapDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const [overtime, heatmap] = await Promise.all([fetchOvertimeData(), fetchFocusHeatmapData()]);
        setOvertimeData(overtime);
        setHeatmapData(heatmap);
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  // --- NEW: Dynamically determine rows and columns from the data ---
  const heatmapApps = [...new Set(heatmapData.map(d => d.day))].sort(); // Get unique app names
  const heatmapMinutes = [...new Set(heatmapData.map(d => d.hour))].sort((a, b) => a - b); // Get unique minutes

  return (
    <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', fontFamily: 'sans-serif' }}>
      <h2 style={{ textAlign: 'center' }}>Key Insights</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div>
          <h3>Overtime Root Cause Drivers</h3>
          {isLoading ? <p>Loading chart...</p> : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={overtimeData} layout="vertical" margin={{ left: 120 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="category" width={120} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="communication_events" stackId="a" fill="#ff7300" name="Communication" />
                <Bar dataKey="execution_events" stackId="a" fill="#3498db" name="Execution" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
        <div>
          <h3>Activity Heatmap (Last Hour by Minute)</h3>
          {isLoading ? <p>Loading heatmap...</p> : (
            <div style={{ display: 'grid', gridTemplateColumns: `repeat(${heatmapApps.length || 1}, 1fr)`, gap: '4px', textAlign: 'center' }}>
              {/* Render App names as columns */}
              {heatmapApps.map(app => <div key={app} style={{ fontWeight: 'bold', fontSize: '10px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={app}>{app}</div>)}
              
              {/* Render a grid for each minute */}
              {heatmapMinutes.map(minute => 
                heatmapApps.map(app => {
                  const dataPoint = heatmapData.find(d => d.day === app && d.hour === minute);
                  const color = dataPoint ? getHeatmapColor(dataPoint.focus_score) : '#efefef';
                  const title = `${app} @ minute ${minute}\nScore: ${dataPoint ? (dataPoint.focus_score * 100).toFixed(0) : 'N/A'}%`;
                  return <div key={`${app}-${minute}`} title={title} style={{ background: color, height: '20px', borderRadius: '3px' }} />;
                })
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductivityInfographic;