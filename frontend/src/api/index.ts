// my-ai-log-viewer/frontend/src/api/index.ts
import axios from 'axios';
import type { LogEntry, FetchLogsOptions, SummarizeResponse } from './types';

// --- MOVED THIS LINE TO THE TOP ---
// Base URL for the API (read from .env or default for remote server)
const API_BASE_URL = import.meta.env.VITE_APP_API_BASE_URL || 'http://192.168.1.214:8001';

// --- fetchLogs FUNCTION (uses URLSearchParams for robustness) ---
export const fetchLogs = async (options: FetchLogsOptions = {}): Promise<LogEntry[]> => {
  try {
    const params = new URLSearchParams();

    if (options.employeeId) {
      params.append('employee_id', options.employeeId);
    }
    if (options.startDate) {
      params.append('start_date', options.startDate);
    }
    if (options.endDate) {
      params.append('end_date', options.endDate);
    }
    if (options.eventType) {
      params.append('event_type', options.eventType);
    }
    if (options.applicationName) {
      params.append('application_name', options.applicationName);
    }
    if (options.limit !== undefined) {
      params.append('limit', String(options.limit));
    }
    if (options.offset !== undefined) {
      params.append('offset', String(options.offset));
    }
    if (options.orderByTimestampDesc !== undefined) {
      params.append('order_by_timestamp_desc', String(options.orderByTimestampDesc));
    }

    // Now this call will work because API_BASE_URL is defined above
    const response = await axios.get<LogEntry[]>(`${API_BASE_URL}/logs/`, { params });
    return response.data;

  } catch (error) {
    console.error("Error fetching logs:", error);
    throw error;
  }
};

// The summarizeLogs function also uses API_BASE_URL
export const summarizeLogs = async (logIds: number[]): Promise<SummarizeResponse> => {
  try {
    const response = await axios.post<SummarizeResponse>(`${API_BASE_URL}/summarize_logs/`, { log_ids: logIds });
    return response.data;
  } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
          console.error("Error summarizing logs (Backend Response):", error.response.data);
          throw new Error(`Failed to summarize: ${JSON.stringify(error.response.data)}`);
      }
    console.error("Error summarizing logs (Network/Unknown):", error);
    throw error;
  }
};
