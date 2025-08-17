// my-ai-log-viewer/frontend/src/components/LogTable.tsx
import React from 'react';
import type { LogEntry } from '../api/types';

interface LogTableProps {
    logs: LogEntry[];
    loading: boolean;
    error: string | null;
    selectedLogIds: Set<number>;
    onLogSelect: (id: number, isSelected: boolean) => void;
}

const LogTable: React.FC<LogTableProps> = ({ logs, loading, error, selectedLogIds, onLogSelect }) => {
    if (loading) {
        return <p>Loading logs...</p>;
    }

    if (error) {
        return <p className="error-message">Error: {error}</p>;
    }

    if (logs.length === 0) {
        return <p>No logs found.</p>;
    }

    return (
        <div className="log-table-container" style={{ maxHeight: '600px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '8px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr style={{ background: '#f2f2f2' }}>
                        <th style={{ ...tableHeaderStyle, width: '30px' }}></th>
                        <th style={tableHeaderStyle}>ID</th>
                        <th style={tableHeaderStyle}>Employee ID</th>
                        <th style={tableHeaderStyle}>Timestamp</th>
                        <th style={tableHeaderStyle}>Event Type</th>
                        <th style={tableHeaderStyle}>Application</th>
                        <th style={tableHeaderStyle}>Window Title</th>
                        <th style={tableHeaderStyle}>Event Detail</th>
                    </tr>
                </thead>
                <tbody>
                    {logs.map((log) => (
                        <tr key={log.id} style={{ background: selectedLogIds.has(log.id) ? '#e0f7fa' : 'white' }}>
                            <td style={tableCellStyle}>
                                <input
                                    type="checkbox"
                                    checked={selectedLogIds.has(log.id)}
                                    onChange={(e) => onLogSelect(log.id, e.target.checked)}
                                />
                            </td>
                            <td style={tableCellStyle}>{log.id}</td>
                            <td style={tableCellStyle}>{log.employee_id}</td>
                            <td style={tableCellStyle}>{new Date(log.timestamp).toLocaleString()}</td>
                            <td style={tableCellStyle}>{log.event_type}</td>
                            <td style={tableCellStyle}>{log.application_name || 'N/A'}</td>
                            <td style={tableCellStyle}>{log.window_title || 'N/A'}</td>
                            <td style={tableCellStyle}>{log.event_detail || 'N/A'}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

const tableHeaderStyle: React.CSSProperties = {
    padding: '8px',
    borderBottom: '1px solid #ddd',
    textAlign: 'left',
    position: 'sticky',
    top: 0,
    background: '#f2f2f2',
    zIndex: 1,
};

const tableCellStyle: React.CSSProperties = {
    padding: '8px',
    borderBottom: '1px solid #ddd',
    textAlign: 'left',
    fontSize: '0.9em',
    wordBreak: 'break-word',
};

export default LogTable;