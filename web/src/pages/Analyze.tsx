import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, CheckCircle } from 'lucide-react';
import FileUploader from '../components/upload/FileUploader';
import ProgressBar from '../components/upload/ProgressBar';
import SettingsPanel from '../components/upload/SettingsPanel';
import { useAnalyze } from '../hooks/useAnalyze';
import { motion } from 'framer-motion';

export default function Analyze() {
  const [logFile, setLogFile] = useState<File | null>(null);
  const [anomaliesFile, setAnomaliesFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState(0.7);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  
  const navigate = useNavigate();
  const { mutate: analyze, isPending, isError, error } = useAnalyze();

  // Симулируем реальный прогресс анализа
  useEffect(() => {
    if (isPending) {
      setProgress(0);
      setProgressStatus('Загрузка файла...');
      
      // Этап 1: Загрузка файла (0-20%)
      const uploadInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 20) {
            clearInterval(uploadInterval);
            setProgressStatus('Парсинг логов...');
            return 20;
          }
          return prev + 5;
        });
      }, 100);

      // Этап 2: Парсинг (20-40%)
      setTimeout(() => {
        const parseInterval = setInterval(() => {
          setProgress(prev => {
            if (prev >= 40) {
              clearInterval(parseInterval);
              setProgressStatus('Загрузка ML модели...');
              return 40;
            }
            return prev + 2;
          });
        }, 150);
      }, 500);

      // Этап 3: Загрузка модели (40-60%)
      setTimeout(() => {
        const modelInterval = setInterval(() => {
          setProgress(prev => {
            if (prev >= 60) {
              clearInterval(modelInterval);
              setProgressStatus('ML-анализ логов...');
              return 60;
            }
            return prev + 2;
          });
        }, 200);
      }, 2000);

      // Этап 4: Анализ (60-90%)
      setTimeout(() => {
        const analyzeInterval = setInterval(() => {
          setProgress(prev => {
            if (prev >= 90) {
              clearInterval(analyzeInterval);
              setProgressStatus('Создание отчета...');
              return 90;
            }
            return prev + 1;
          });
        }, 300);
      }, 5000);

      // Этап 5: Генерация отчета (90-100%)
      setTimeout(() => {
        const reportInterval = setInterval(() => {
          setProgress(prev => {
            if (prev >= 100) {
              clearInterval(reportInterval);
              setProgressStatus('Готово!');
              return 100;
            }
            return prev + 2;
          });
        }, 200);
      }, 15000);

      return () => {
        // Очистка всех интервалов при размонтировании
        setProgress(0);
        setProgressStatus('');
      };
    }
  }, [isPending]);

  const handleFileSelect = (file: File, type: 'logs' | 'anomalies') => {
    if (type === 'logs') {
      setLogFile(file);
    } else {
      setAnomaliesFile(file);
    }
  };

  const handleFileRemove = (type: 'logs' | 'anomalies') => {
    if (type === 'logs') {
      setLogFile(null);
    } else {
      setAnomaliesFile(null);
    }
  };

  const handleAnalyze = () => {
    if (!logFile) return;

    console.log('🚀 Отправляю анализ с threshold:', threshold);

    analyze(
      {
        logFile,
        anomaliesFile,
        threshold,
      },
      {
        onSuccess: (data) => {
          // Сохраняем в историю (БЕЗ HTML графиков чтобы не переполнить localStorage)
          const historyItem = {
            id: `${Date.now()}`,
            timestamp: new Date().toISOString(),
            filename: logFile.name,
            data: {
              status: data.status,
              analysis: data.analysis,
              results: data.results,
              excel_report: data.excel_report,
              // Графики НЕ сохраняем - они генерируются каждый раз
            },
          };

          const saved = localStorage.getItem('analysis_history');
          const history = saved ? JSON.parse(saved) : [];
          history.unshift(historyItem); // Добавляем в начало
          localStorage.setItem('analysis_history', JSON.stringify(history.slice(0, 50))); // Сохраняем последние 50

          console.log('✅ Анализ завершен! Полученный threshold:', data.analysis.threshold_used);
          navigate('/results', { state: { data, error: null } });
        },
        onError: (error) => {
          // Navigate to results page with error
          console.error('❌ Ошибка анализа:', error);
          navigate('/results', { state: { data: null, error: error.message } });
        },
      }
    );
  };

  const canAnalyze = logFile && !isPending;

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto max-w-5xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Анализ логов
          </h1>
          <p className="text-xl text-gray-400">
            Загрузите файлы и получите детальный отчет за секунды
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Main content */}
          <div className="md:col-span-2 space-y-6">
            {/* File uploader */}
            <div>
              <FileUploader
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
                logFile={logFile}
                anomaliesFile={anomaliesFile}
                disabled={isPending}
              />
            </div>

            {/* Progress */}
            {isPending && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="card"
              >
                <ProgressBar
                  progress={progress}
                  status={progressStatus}
                />
              </motion.div>
            )}

            {/* Error */}
            {isError && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="card border-red-500/50 bg-red-500/10"
              >
                <div className="flex items-start space-x-3">
                  <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-red-400">Ошибка анализа</h3>
                    <p className="text-red-300/80 mt-1">
                      {error?.message || 'Произошла ошибка при анализе файлов'}
                    </p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Analyze button */}
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              onClick={handleAnalyze}
              disabled={!canAnalyze}
              className={`
                w-full py-4 rounded-xl font-semibold text-lg transition-all
                ${canAnalyze
                  ? 'bg-gradient-to-r from-atomic-blue to-atomic-accent text-white hover:shadow-xl hover:shadow-atomic-blue/50'
                  : 'bg-gray-700 text-gray-400 cursor-not-allowed'
                }
              `}
            >
              {isPending ? 'Анализируем...' : 'Начать анализ'}
            </motion.button>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Settings */}
            <div>
              <SettingsPanel
                threshold={threshold}
                onThresholdChange={setThreshold}
                disabled={isPending}
              />
            </div>

            {/* Info card */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="card bg-atomic-blue/10 border-atomic-blue/30"
            >
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-6 h-6 text-atomic-accent flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    Что вы получите
                  </h3>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-atomic-accent"></span>
                      <span>Список всех аномалий и проблем</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-atomic-accent"></span>
                      <span>Интерактивные графики</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-atomic-accent"></span>
                      <span>Детальную статистику</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-atomic-accent"></span>
                      <span>Excel отчет для экспорта</span>
                    </li>
                  </ul>
                </div>
              </div>
            </motion.div>

            {/* Example files */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="card"
            >
              <h3 className="text-sm font-semibold text-gray-300 mb-3">
                Примеры файлов
              </h3>
              <div className="space-y-2">
                <a
                  href="#"
                  className="block p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 text-sm text-gray-400 hover:text-white transition-colors"
                >
                  📄 example_logs.txt
                </a>
                <a
                  href="#"
                  className="block p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 text-sm text-gray-400 hover:text-white transition-colors"
                >
                  📦 example_archive.zip
                </a>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}

