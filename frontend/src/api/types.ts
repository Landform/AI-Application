// my-ai-log-viewer/frontend/src/api/types.ts

// Interface for log entries fetched from the backend
export interface LogEntry {
  id: number;
  employee_id: string;
  timestamp: string; // ISO string
  event_type: string;
  application_name?: string;
  window_title?: string;
  event_detail?: string;
  screenshot_path?: string;
}

// Interface for options when fetching logs
export interface FetchLogsOptions {
  employeeId?: string;
  startDate?: string;
  endDate?: string;
  eventType?: string;
  applicationName?: string;
  limit?: number;
  offset?: number;
  orderByTimestampDesc?: boolean;
}

// Interface for the AI summarization response
export interface SummarizeResponse {
  employee_id: string;
  num_logs_summarized: number;
  summary: string;
}