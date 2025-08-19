// my-ai-log-viewer/frontend/src/App.tsx
import { useState, useEffect } from 'react';
import { fetchLogs, summarizeLogs } from './api';
import type { LogEntry } from './api/types';
import LogTable from './components/LogTable';
import './App.css';

function App() {
  // --- State for Filters that have UI inputs ---
  const [employeeIdFilter, setEmployeeIdFilter] = useState<string>('');
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('');
  const [applicationNameFilter, setApplicationNameFilter] = useState<string>('');

  // --- State/Constants for filters without UI inputs in this version ---
  // We remove the "setter" functions (e.g., setLimit) to avoid "unused variable" errors.
  const [limit] = useState<number>(100);
  const [offset, setOffset] = useState<number>(0); // Keep setter for pagination
  const [orderByDesc] = useState<boolean>(true);
  const [startDateFilter] = useState<string>(''); // Not used in current UI
  const [endDateFilter] = useState<string>('');   // Not used in current UI

  // --- State for Data and UI ---
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLogIds, setSelectedLogIds] = useState<Set<number>>(new Set());
  const [summary, setSummary] = useState<string>('');
  const [summarizing, setSummarizing] = useState<boolean>(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);


  // --- Data Fetching Logic ---
  const loadLogs = async () => {
    setLoading(true);
    setError(null);

    const filterOptions = {
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
    } catch (e: any) {
      setError(e.message || 'An unknown error occurred');
      console.error("Error catched in loadLogs:", e);
    } finally {
      setLoading(false);
    }
  };

  // This useEffect re-fetches data when the offset changes (for pagination)
  useEffect(() => {
    loadLogs();
  }, [offset]);

  // --- Summarization Logic ---
  const handleSummarize = async () => {
    setSummary(''); setSummaryError(null); setSummarizing(true);
    if(selectedLogIds.size === 0) { setSummaryError("Please select logs."); setSummarizing(false); return; }
    try {
      const result = await summarizeLogs(Array.from(selectedLogIds));
      if(result && result.summary) { setSummary(result.summary); }
      else { setSummaryError("Received response with no summary."); }
    } catch(e: any) {
      setSummaryError(e.message || "Unknown summarization error.");
    } finally { setSummarizing(false); }
  }
  
  // --- Pagination Handlers ---
  const handlePrevPage = () => setOffset(prev => Math.max(0, prev - limit));
  const handleNextPage = () => { if (logs.length === limit) setOffset(prev => prev + limit); };


  // --- JSX Rendering ---
  return (
    <div className="App" style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Employee Activity Logs</h1>

      <div style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '15px', borderRadius: '8px', background: '#f9f9f9' }}>
        <h2>Filters</h2>
        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', alignItems: 'flex-end', marginBottom: '15px' }}>
          
          {/* Employee ID Filter */}
          <div>
            <label htmlFor="employeeId" style={{ display: 'block', paddingBottom: '4px' }}>Employee ID:</label>
            <input
              id="employeeId"
              type="text"
              value={employeeIdFilter}
              onChange={(e) => setEmployeeIdFilter(e.target.value)}
              placeholder="e.g., karanesh"
            />
          </div>

          {/* Event Type Filter */}
          <div>
            <label htmlFor="eventType" style={{ display: 'block', paddingBottom: '4px' }}>Event Type:</label>
            <input
              id="eventType"
              type="text"
              value={eventTypeFilter}
              onChange={(e) => setEventTypeFilter(e.target.value)}
              placeholder="e.g., keyboard"
            />
          </div>

          {/* Application Name Filter */}
          <div>
            <label htmlFor="applicationName" style={{ display: 'block', paddingBottom: '4px' }}>Application Name:</label>
            <input
              id="applicationName"
              type="text"
              value={applicationNameFilter}
              onChange={(e) => setApplicationNameFilter(e.target.value)}
              placeholder="e.g., Code.exe"
            />
          </div>
          
          <button onClick={loadLogs} disabled={loading} style={{ padding: '5px 10px', height: '30px' }}>
            {loading ? 'Searching...' : 'Apply Filters'}
          </button>
        </div>
      </div>

      {/* Summarize Section */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={handleSummarize} disabled={selectedLogIds.size === 0 || summarizing}>
          {summarizing ? 'Summarizing...' : `Summarize Selected (${selectedLogIds.size})`}
        </button>
        {summaryError && <p style={{ color: 'red' }}>{summaryError}</p>}
        {summary && <div style={{ border: '1px solid #007bff', padding: '10px', marginTop: '10px' }}><h2>AI Summary</h2><p>{summary}</p></div>}
      </div>

      {/* Log Table */}
      <LogTable logs={logs} loading={loading} error={error} selectedLogIds={selectedLogIds} onLogSelect={(id, isSelected) => setSelectedLogIds(prev => { const next = new Set(prev); isSelected ? next.add(id) : next.delete(id); return next; })} />

      {/* Pagination Section */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
        <button onClick={handlePrevPage} disabled={offset === 0 || loading}>Previous Page</button>
        <span>Page Offset: {offset}</span>
        <button onClick={handleNextPage} disabled={logs.length < limit || loading}>Next Page</button>
      </div>
    </div>
  );
}

export default App;
