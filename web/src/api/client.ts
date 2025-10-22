import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for large file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface AnalysisResult {
  'ID аномалии': number;
  'ID проблемы': number;
  'Файл с проблемой': string;
  '№ строки': number;
  'Строка из лога': string;
}

export interface BasicStats {
  total_lines: number;
  error_count: number;
  warning_count: number;
  info_count: number;
  sources: Record<string, number>;
  time_range?: {
    start: string;
    end: string;
  };
  top_messages: Record<string, number>;
  level_distribution: Record<string, number>;
}

export interface MLResults {
  total_problems: number;
  unique_anomalies: number;
  unique_problems: number;
  unique_files: number;
}

export interface AnalyzeResponse {
  status: string;
  analysis: {
    basic_stats: BasicStats;
    ml_results: MLResults;
    threshold_used: number;
  };
  results: AnalysisResult[];
  excel_report: string | null;
}

// API Methods
export const analyzeLogsAPI = async (
  logFile: File,
  anomaliesFile?: File | null,
  threshold: number = 0.7
): Promise<AnalyzeResponse> => {
  const formData = new FormData();
  formData.append('log_file', logFile);
  if (anomaliesFile) {
    formData.append('anomalies_file', anomaliesFile);
  }
  formData.append('threshold', threshold.toString());

  console.log('📤 Отправка запроса на анализ:', {
    fileName: logFile.name,
    fileSize: logFile.size,
    threshold
  });

  try {
    const response = await api.post<AnalyzeResponse>('/api/v1/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 300000, // 5 минут для больших файлов
    });

    console.log('✅ Ответ от API:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ Ошибка API:', error);
    throw new Error(error.response?.data?.detail || error.message || 'Ошибка анализа');
  }
};

export const downloadExcel = async (filename: string): Promise<Blob> => {
  const response = await api.get(`/api/v1/download/${filename}`, {
    responseType: 'blob',
  });
  return response.data;
};

export const getDefaultAnomalies = async (): Promise<Blob> => {
  const response = await api.get('/api/v1/anomalies/default', {
    responseType: 'blob',
  });
  return response.data;
};

export const healthCheck = async (): Promise<any> => {
  const response = await api.get('/health');
  return response.data;
};

export default api;

