// my-ai-log-viewer/frontend/src/api/index.ts
// Import all types/interfaces from the new types.ts file
import axios from 'axios';
import type { LogEntry, FetchLogsOptions, SummarizeResponse } from './types'; // Corrected import path

// Function to fetch logs from the backend
export const fetchLogs = async (options: FetchLogsOptions = {}): Promise<LogEntry[]> => {
  try {
    const params: Record<string, any> = {};
    if (options.employeeId) params.employee_id = options.employeeId;
    if (options.startDate) params.start_date = options.startDate;
    if (options.endDate) params.end_date = options.endDate; // Corrected to use 'end_date' for the backend parameter
    if (options.eventType) params.event_type = options.eventType;
    if (options.applicationName) params.application_name = options.applicationName;
    if (options.limit) params.limit = options.limit;
    if (options.offset) params.offset = options.offset;
    if (options.orderByTimestampDesc !== undefined) params.order_by_timestamp_desc = options.orderByTimestampDesc;

    const response = await axios.get<LogEntry[]>(`${API_BASE_URL}/logs/`, { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching logs:", error);
    throw error;
  }
};

// Function to summarize logs using the backend AI
export const summarizeLogs = async (logIds: number[]): Promise<SummarizeResponse> => {
  try {
    const response = await axios.post<SummarizeResponse>(`${API_BASE_URL}/summarize_logs/`, { log_ids: logIds });
    return response.data;
  } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
          console.error("Error summarizing logs (Backend Response):", error.response.data);
          throw new Error(`Failed to summarize: ${error.response.data.detail || error.response.statusText}`);
      }
    console.error("Error summarizing logs (Network/Unknown):", error);
    throw error;
  }
};

// Base URL for the API (read from .env or default for local development)
const API_BASE_URL = import.meta.env.VITE_APP_API_BASE_URL || 'http://localhost:8000';