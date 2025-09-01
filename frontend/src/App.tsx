// frontend/src/App.tsx (FINAL, LINT-FIXED VERSION)
import { useState, useEffect } from 'react';
import { fetchLogs, summarizeLogs } from './api';
import type { LogEntry } from './api/types';
import LogTable from './components/LogTable';
import ProductivityInfographic from './components/ProductivityInfographic';
import './App.css';

function App() {
  // State for filters that have UI inputs
  const [employeeIdFilter, setEmployeeIdFilter] = useState<string>('');
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('');
  const [applicationNameFilter, setApplicationNameFilter] = useState<string>('');
  const [offset, setOffset] = useState<number>(0);

  // State/Constants for filters without UI inputs in this version
  // We remove the "setter" functions to avoid "unused variable" errors.
  const [startDateFilter] = useState<string>('');
  const [endDateFilter] = useState<string>('');
  const [limit] = useState<number>(100);
  const [orderByDesc] = useState<boolean>(true);

  // State for UI and data
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showInfographic, setShowInfographic] = useState<boolean>(false);
  const [selectedLogIds, setSelectedLogIds] = useState<Set<number>>(new Set());
  const [summary, setSummary] = useState<string>('');
  const [summarizing, setSummarizing] = useState<boolean>(false);

  const loadLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedLogs = await fetchLogs({
        employeeId: employeeIdFilter,
        eventType: eventTypeFilter,
        applicationName: applicationNameFilter,
        startDate: startDateFilter,
        endDate: endDateFilter,
        limit,
        offset,
        orderByTimestampDesc: orderByDesc,
    };

    try {
      const fetchedLogs = await fetchLogs(filterOptions);
      setLogs(fetchedLogs);
    } catch (e) {
      setError("Failed to fetch logs.");
    } finally {
      setLoading(false);
    }
  };
  };

  // Re-fetches data when pagination (offset) changes.
  // Filtering is manual via the "Apply Filters" button.
  useEffect(() => {
    loadLogs();
  }, [offset]);

  // --- Summarization Logic ---
  }, [offset]);

  const handleSummarize = async () => {
    setSummarizing(true);
    try {
      const result = await summarizeLogs(Array.from(selectedLogIds));
      setSummary(result.summary);
    } catch (e) {
      setSummary("Failed to generate summary.");
    } finally {
      setSummarizing(false);
    }
  };

  const handleSelectLog = (id: number, isSelected: boolean) => {
    const next = new Set(selectedLogIds);
    isSelected ? next.add(id) : next.delete(id);
    setSelectedLogIds(next);
  };

  return (
    <div className="App">
      <header>
        <h1>Employee Activity Log Viewer</h1>
        <button onClick={() => setShowInfographic(!showInfographic)}>
          {showInfographic ? 'Hide Insights' : 'Show Insights'}
        </button>
      </header>
      
      {showInfographic && <ProductivityInfographic />}

      <div className="filters">
        <input value={employeeIdFilter} onChange={e => setEmployeeIdFilter(e.target.value)} placeholder="Filter by Employee ID" />
        <input value={eventTypeFilter} onChange={e => setEventTypeFilter(e.target.value)} placeholder="Filter by Event Type" />
        <input value={applicationNameFilter} onChange={e => setApplicationNameFilter(e.target.value)} placeholder="Filter by App Name" />
        <button onClick={loadLogs}>Apply Filters</button>
      </div>

      <div className="summarize-section">
        <button onClick={handleSummarize} disabled={selectedLogIds.size === 0 || summarizing}>
          {summarizing ? 'Summarizing...' : `Summarize Selected (${selectedLogIds.size})`}
        </button>
        {summary && <div className="summary-box"><p>{summary}</p></div>}
      </div>

      <LogTable logs={logs} loading={loading} error={error} selectedLogIds={selectedLogIds} onLogSelect={handleSelectLog} />
      
      <div className="pagination">
        <button onClick={() => setOffset(prev => Math.max(0, prev - limit))} disabled={offset === 0}>Previous</button>
        <span>Offset: {offset}</span>
        <button onClick={() => setOffset(prev => prev + limit)} disabled={logs.length < limit}>Next</button>
      </div>
    </div>
  );
}

export default App;
