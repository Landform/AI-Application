// frontend/src/api/index.ts
import axios from 'axios';
import type { LogEntry, FetchLogsOptions, SummarizeResponse, OvertimeDataPoint, HeatmapDataPoint } from './types';

const API_BASE_URL = import.meta.env.VITE_APP_API_BASE_URL || 'http://192.168.1.214:8001';

export const fetchLogs = async (options: FetchLogsOptions = {}): Promise<LogEntry[]> => {
  try {
    const params = {
      employee_id: options.employeeId,
      event_type: options.eventType,
      application_name: options.applicationName,
      start_date: options.startDate, // ADDED BACK
      end_date: options.endDate,     // ADDED BACK
      limit: options.limit,
      offset: options.offset,
      order_by_timestamp_desc: options.orderByTimestampDesc,
    };
    const response = await axios.get<LogEntry[]>(`${API_BASE_URL}/logs/`, { params });
    return response.data;

  } catch (error) {
    console.error("Error fetching logs:", error);
    throw error;
  }
};

export const summarizeLogs = async (logIds: number[]): Promise<SummarizeResponse> => {
  try {
    const response = await axios.post<SummarizeResponse>(`${API_BASE_URL}/summarize_logs/`, { log_ids: logIds });
    return response.data;
  } catch (error) {
    console.error("Error summarizing logs:", error);
    throw error;
  }
};

export const fetchOvertimeData = async (): Promise<OvertimeDataPoint[]> => {
  try {
    const response = await axios.get<OvertimeDataPoint[]>(`${API_BASE_URL}/api/dashboard/overtime-analysis`);
    return response.data;
  } catch (error) {
    console.error("Error fetching overtime data:", error);
    throw error;
  }
};

export const fetchFocusHeatmapData = async (): Promise<HeatmapDataPoint[]> => {
  try {
    const response = await axios.get<HeatmapDataPoint[]>(`${API_BASE_URL}/api/dashboard/focus-heatmap`);
    return response.data;
  } catch (error) {
    console.error("Error fetching heatmap data:", error);
    throw error;
  }
};