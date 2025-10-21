import { useMutation } from '@tanstack/react-query';
import { analyzeLogsAPI } from '../api/client';
import type { AnalyzeResponse } from '../api/client';

interface AnalyzeParams {
  logFile: File;
  anomaliesFile?: File | null;
  threshold?: number;
}

export const useAnalyze = () => {
  return useMutation<AnalyzeResponse, Error, AnalyzeParams>({
    mutationFn: async ({ logFile, anomaliesFile, threshold = 0.7 }: AnalyzeParams) => {
      return await analyzeLogsAPI(logFile, anomaliesFile, threshold);
    },
  });
};

