// frontend/src/api/types.ts
export interface LogEntry {
  id: number;
  employee_id: string;
  timestamp: string;
  event_type: string;
  application_name?: string;
  window_title?: string;
  event_detail?: string;
}

export interface FetchLogsOptions {
  employeeId?: string;
  eventType?: string;
  applicationName?: string;
  startDate?: string; // ADDED BACK
  endDate?: string;   // ADDED BACK
  limit?: number;
  offset?: number;
  orderByTimestampDesc?: boolean;
}

export interface SummarizeResponse {
  summary: string;
}

export interface OvertimeDataPoint {
  category: string;
  execution_events: number;
  communication_events: number;
}

export interface HeatmapDataPoint {
  day: string;
  hour: number;
  focus_score: number;
}