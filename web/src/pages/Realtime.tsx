import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Play, Square, Upload, AlertTriangle, CheckCircle, Clock, FileText } from 'lucide-react';

interface RealtimeStats {
  lines_processed: number;
  errors_found: number;
  warnings_found: number;
  anomalies_found: number;
}

interface Anomaly {
  id: string;
  type: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  line_number: number;
}

interface Notification {
  id: string;
  type: 'anomaly' | 'error' | 'warning' | 'progress';
  message: string;
  timestamp: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
}

export default function Realtime() {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [stats, setStats] = useState<RealtimeStats>({
    lines_processed: 0,
    errors_found: 0,
    warnings_found: 0,
    anomalies_found: 0
  });
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [fileInput, setFileInput] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const websocketRef = useRef<WebSocket | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Очистка уведомлений старше 5 минут
  useEffect(() => {
    const interval = setInterval(() => {
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
      setNotifications(prev => 
        prev.filter(notif => new Date(notif.timestamp) > fiveMinutesAgo)
      );
    }, 60000); // Каждую минуту

    return () => clearInterval(interval);
  }, []);

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date().toISOString()
    };
    
    setNotifications(prev => [newNotification, ...prev.slice(0, 49)]); // Максимум 50 уведомлений
  };

  const connectWebSocket = (sessionId: string) => {
    const wsUrl = `ws://localhost:8000/api/v1/stream/${sessionId}`;
    console.log('🔌 Подключение к WebSocket:', wsUrl);
    
    const ws = new WebSocket(wsUrl);
    websocketRef.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket подключен');
      addNotification({
        type: 'progress',
        message: 'Подключение к мониторингу установлено',
        severity: 'low'
      });
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 Получено сообщение:', data);

        if (data.type === 'stats') {
          setStats(data.data);
          addNotification({
            type: 'progress',
            message: `Обработано ${data.data.lines_processed} строк`,
            severity: 'low'
          });
        } else if (data.type === 'anomaly') {
          const anomaly: Anomaly = {
            id: data.data.id || Date.now().toString(),
            type: data.data.type || 'Unknown',
            description: data.data.description || 'Аномалия обнаружена',
            severity: data.data.severity || 'medium',
            timestamp: data.data.timestamp || new Date().toISOString(),
            line_number: data.data.line_number || 0
          };
          
          setAnomalies(prev => [anomaly, ...prev]);
          addNotification({
            type: 'anomaly',
            message: `Обнаружена аномалия: ${anomaly.description}`,
            severity: anomaly.severity
          });
        } else if (data.type === 'error') {
          addNotification({
            type: 'error',
            message: data.message || 'Ошибка при обработке',
            severity: 'high'
          });
        }
      } catch (err) {
        console.error('❌ Ошибка парсинга WebSocket сообщения:', err);
      }
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket отключен');
      addNotification({
        type: 'progress',
        message: 'Соединение с мониторингом потеряно',
        severity: 'medium'
      });
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket ошибка:', error);
      addNotification({
        type: 'error',
        message: 'Ошибка соединения с сервером',
        severity: 'high'
      });
    };
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Проверяем тип файла
      const allowedTypes = ['.txt', '.log', '.zip'];
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      
      if (!allowedTypes.includes(fileExtension)) {
        setError('Поддерживаются только файлы .txt, .log, .zip');
        return;
      }
      
      setFileInput(file);
      setError(null);
    }
  };

  const startMonitoring = async () => {
    if (!fileInput) {
      setError('Выберите файл для анализа');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('log_file', fileInput);

      console.log('📤 Загрузка файла для реал-тайм мониторинга...');
      
      const response = await fetch('http://localhost:8000/api/v1/stream/start', {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(30000) // 30 секунд таймаут
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ Файл загружен, получен session_id:', result.session_id);
      
      setSessionId(result.session_id);
      setIsMonitoring(true);
      addNotification({
        type: 'progress',
        message: 'Мониторинг запущен',
        severity: 'low'
      });

      // Подключаемся к WebSocket
      connectWebSocket(result.session_id);

    } catch (err) {
      console.error('❌ Ошибка запуска мониторинга:', err);
      setError(`Ошибка запуска мониторинга: ${err}`);
    } finally {
      setIsUploading(false);
    }
  };

  const stopMonitoring = async () => {
    if (!sessionId) return;

    try {
      await fetch(`http://localhost:8000/api/v1/stream/stop/${sessionId}`, {
        method: 'POST'
      });
      
      if (websocketRef.current) {
        websocketRef.current.close();
        websocketRef.current = null;
      }
      
      setIsMonitoring(false);
      setSessionId(null);
      addNotification({
        type: 'progress',
        message: 'Мониторинг остановлен',
        severity: 'low'
      });
    } catch (err) {
      console.error('❌ Ошибка остановки мониторинга:', err);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'high': return 'text-orange-400 bg-orange-400/10 border-orange-400/20';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'low': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="w-4 h-4" />;
      case 'high': return <AlertTriangle className="w-4 h-4" />;
      case 'medium': return <Clock className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-atomic-dark py-8">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-6xl mx-auto"
        >
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-4">
              Реал-тайм мониторинг логов
            </h1>
            <p className="text-gray-400 text-lg">
              Анализ логов в реальном времени с обнаружением аномалий
            </p>
          </div>

          {/* Загрузка файла */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card mb-8"
          >
            <h2 className="text-xl font-bold text-white mb-4">Загрузка файла</h2>
            
            <div className="space-y-4">
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.log,.zip"
                onChange={handleFileUpload}
                className="hidden"
              />
              
              <button
                onClick={() => fileInputRef.current?.click()}
                className="btn btn-primary w-full"
                disabled={isMonitoring}
              >
                <Upload className="w-5 h-5 mr-2" />
                {fileInput ? fileInput.name : 'Выберите файл (.txt, .log, .zip)'}
              </button>

              {fileInput && (
                <div className="flex space-x-4">
                  <button
                    onClick={startMonitoring}
                    disabled={isUploading || isMonitoring}
                    className="btn btn-success flex-1"
                  >
                    {isUploading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Загрузка...
                      </>
                    ) : (
                      <>
                        <Play className="w-5 h-5 mr-2" />
                        Запустить мониторинг
                      </>
                    )}
                  </button>

                  {isMonitoring && (
                    <button
                      onClick={stopMonitoring}
                      className="btn btn-danger"
                    >
                      <Square className="w-5 h-5 mr-2" />
                      Остановить
                    </button>
                  )}
                </div>
              )}

              {error && (
                <div className="text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg p-3">
                  {error}
                </div>
              )}
            </div>
          </motion.div>

          {/* Статистика */}
          {isMonitoring && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
            >
              <div className="card text-center">
                <div className="text-2xl font-bold text-blue-400">{stats.lines_processed.toLocaleString()}</div>
                <div className="text-gray-400">Обработано строк</div>
              </div>
              <div className="card text-center">
                <div className="text-2xl font-bold text-red-400">{stats.errors_found}</div>
                <div className="text-gray-400">Ошибок</div>
              </div>
              <div className="card text-center">
                <div className="text-2xl font-bold text-yellow-400">{stats.warnings_found}</div>
                <div className="text-gray-400">Предупреждений</div>
              </div>
              <div className="card text-center">
                <div className="text-2xl font-bold text-purple-400">{stats.anomalies_found}</div>
                <div className="text-gray-400">Аномалий</div>
              </div>
            </motion.div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Уведомления */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card"
            >
              <h3 className="text-lg font-bold text-white mb-4">Уведомления</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="text-gray-400 text-center py-8">
                    Уведомления появятся здесь
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <motion.div
                      key={notification.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={`p-3 rounded-lg border ${getSeverityColor(notification.severity || 'low')}`}
                    >
                      <div className="flex items-start space-x-2">
                        {getSeverityIcon(notification.severity || 'low')}
                        <div className="flex-1">
                          <div className="text-sm font-medium">{notification.message}</div>
                          <div className="text-xs opacity-70">
                            {new Date(notification.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            </motion.div>

            {/* Аномалии */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="card"
            >
              <h3 className="text-lg font-bold text-white mb-4">Обнаруженные аномалии</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {anomalies.length === 0 ? (
                  <div className="text-gray-400 text-center py-8">
                    Аномалии будут отображаться здесь
                  </div>
                ) : (
                  anomalies.map((anomaly) => (
                    <motion.div
                      key={anomaly.id}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={`p-3 rounded-lg border ${getSeverityColor(anomaly.severity)}`}
                    >
                      <div className="flex items-start space-x-2">
                        {getSeverityIcon(anomaly.severity)}
                        <div className="flex-1">
                          <div className="text-sm font-medium">{anomaly.description}</div>
                          <div className="text-xs opacity-70">
                            Строка {anomaly.line_number} • {new Date(anomaly.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
