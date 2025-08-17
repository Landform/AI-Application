// my-ai-log-viewer/frontend/src/App.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { fetchLogs, summarizeLogs } from './api'; // fetchLogs and summarizeLogs are values (functions)
import type { LogEntry } from './api/types'; // LogEntry is a type (interface)
import LogTable from './components/LogTable';
import './App.css';

function App() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [employeeIdFilter, setEmployeeIdFilter] = useState<string>('');
  const [startDateFilter, setStartDateFilter] = useState<string>('');
  const [endDateFilter, setEndDateFilter] = useState<string>('');
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('');
  const [applicationNameFilter, setApplicationNameFilter] = useState<string>('');
  const [limit, setLimit] = useState<number>(100);
  const [offset, setOffset] = useState<number>(0);
  const [orderByDesc, setOrderByDesc] = useState<boolean>(true);

  const [selectedLogIds, setSelectedLogIds] = useState<Set<number>>(new Set());
  const [summary, setSummary] = useState<string>('');
  const [summarizing, setSummarizing] = useState<boolean>(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedLogs = await fetchLogs({
        employeeId: employeeIdFilter || undefined,
        startDate: startDateFilter || undefined,
        endDate: endDateFilter || undefined,
        eventType: eventTypeFilter || undefined,
        applicationName: applicationNameFilter || undefined,
        limit,
        offset,
        orderByTimestampDesc: orderByDesc,
      });
      setLogs(fetchedLogs);
      setSelectedLogIds(new Set());
      setSummary('');
    } catch (e: any) {
      setError(e.message || 'An unknown error occurred');
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [employeeIdFilter, startDateFilter, endDateFilter, eventTypeFilter, applicationNameFilter, limit, offset, orderByDesc]);


  useEffect(() => {
    loadLogs();
  }, [loadLogs]);


  const handlePrevPage = () => {
    setOffset(prev => Math.max(0, prev - limit));
  };

  const handleNextPage = () => {
    if (logs.length === limit) {
      setOffset(prev => prev + limit);
    }
  };

  const handleLogSelect = (id: number, isSelected: boolean) => {
    setSelectedLogIds(prev => {
      const newSet = new Set(prev);
      if (isSelected) {
        newSet.add(id);
      } else {
        newSet.delete(id);
      }
      return newSet;
    });
  };

  const handleSummarize = async () => {
    if (selectedLogIds.size === 0) {
      setSummaryError("Please select at least one log entry to summarize.");
      setSummary('');
      return;
    }

    setSummarizing(true);
    setSummaryError(null);
    setSummary('');

    try {
      const idsToSummarize = Array.from(selectedLogIds);
      const result = await summarizeLogs(idsToSummarize);
      setSummary(result.summary);
    } catch (e: any) {
      setSummaryError(e.response?.data?.detail || e.message || "Failed to generate summary.");
      console.error("Summarization error:", e);
    } finally {
      setSummarizing(false);
    }
  };

  return (
    <div className="App" style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Employee Activity Logs</h1>

      <div style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '15px', borderRadius: '8px', background: '#f9f9f9' }}>
        <h2>Filters</h2>
        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', alignItems: 'flex-end', marginBottom: '15px' }}>
          <div>
            <label htmlFor="employeeId" style={{ display: 'block', marginBottom: '5px' }}>Employee ID:</label>
            <input
              type="text"
              id="employeeId"
              value={employeeIdFilter}
              onChange={(e) => setEmployeeIdFilter(e.target.value)}
              placeholder="e.g., john.doe"
              style={inputStyle}
            />
          </div>
          <div>
            <label htmlFor="startDate" style={{ display: 'block', marginBottom: '5px' }}>Start Date (YYYY-MM-DDTHH:MM):</label>
            <input
              type="datetime-local"
              id="startDate"
              value={startDateFilter}
              onChange={(e) => setStartDateFilter(e.target.value)}
              placeholder="e.g., 2023-01-01T00:00"
              style={inputStyle}
            />
          </div>
          <div>
            <label htmlFor="endDate" style={{ display: 'block', marginBottom: '5px' }}>End Date (YYYY-MM-DDTHH:MM):</label>
            <input
              type="datetime-local"
              id="endDate"
              value={endDateFilter}
              onChange={(e) => setEndDateFilter(e.target.value)}
              placeholder="e.g., 2023-01-31T23:59"
              style={inputStyle}
            />
          </div>
          <div>
            <label htmlFor="eventType" style={{ display: 'block', marginBottom: '5px' }}>Event Type:</label>
            <input
              type="text"
              id="eventType"
              value={eventTypeFilter}
              onChange={(e) => setEventTypeFilter(e.target.value)}
              placeholder="e.g., keyboard, mouse_click"
              style={inputStyle}
            />
          </div>
            <div>
            <label htmlFor="applicationName" style={{ display: 'block', marginBottom: '5px' }}>Application Name:</label>
            <input
                type="text"
                id="applicationName"
                value={applicationNameFilter}
                onChange={(e) => setApplicationNameFilter(e.target.value)}
                placeholder="e.g., chrome, vscode"
                style={inputStyle}
            />
          </div>
          <div>
            <label htmlFor="limit" style={{ display: 'block', marginBottom: '5px' }}>Limit:</label>
            <input
              type="number"
              id="limit"
              value={limit}
              onChange={(e) => setLimit(Math.max(1, parseInt(e.target.value) || 1))}
              min="1"
              max="1000"
              style={{ ...inputStyle, width: '80px' }}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <input
              type="checkbox"
              id="orderByDesc"
              checked={orderByDesc}
              onChange={(e) => setOrderByDesc(e.target.checked)}
              style={{ marginRight: '5px' }}
            />
            <label htmlFor="orderByDesc">Newest first</label>
          </div>
          <button onClick={loadLogs} style={buttonStyle}>Apply Filters</button>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button
          onClick={handleSummarize}
          disabled={selectedLogIds.size === 0 || summarizing}
          style={{ ...buttonStyle, background: '#28a745', marginRight: '10px' }}
        >
          {summarizing ? 'Summarizing...' : `Summarize Selected (${selectedLogIds.size}) Logs`}
        </button>
        {summaryError && <p style={{ color: 'red', marginTop: '10px' }}>{summaryError}</p>}
        {summary && (
          <div style={{ border: '1px solid #007bff', padding: '15px', borderRadius: '8px', marginTop: '15px', background: '#e6f7ff' }}>
            <h2>AI Summary</h2>
            <p>{summary}</p>
          </div>
        )}
      </div>

      <LogTable
        logs={logs}
        loading={loading}
        error={error}
        selectedLogIds={selectedLogIds}
        onLogSelect={handleLogSelect}
      />

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
        <button onClick={handlePrevPage} disabled={offset === 0 || loading} style={buttonStyle}>
          Previous Page
        </button>
        <span style={{ margin: '0 10px', lineHeight: '38px' }}>Page Offset: {offset}</span>
        <button onClick={handleNextPage} disabled={logs.length < limit || loading} style={buttonStyle}>
          Next Page
        </button>
      </div>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  padding: '8px',
  border: '1px solid #ccc',
  borderRadius: '4px',
  width: '180px',
};

const buttonStyle: React.CSSProperties = {
  padding: '10px 15px',
  background: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '1em',
  whiteSpace: 'nowrap'
};

export default App;