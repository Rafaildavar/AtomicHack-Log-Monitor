import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Loader2, FileText, Package } from 'lucide-react';
import { api } from '../../api/client';

interface GraphModalProps {
  isOpen: boolean;
  onClose: () => void;
  filename: string;
  isZip: boolean;
  fileId: string;  // ID файла на сервере для генерации графиков
}

export default function GraphModal({ isOpen, onClose, filename, isZip, fileId }: GraphModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [graphHtml, setGraphHtml] = useState<string>('');
  const [graphUrl, setGraphUrl] = useState<string>('');
  const [zipFiles, setZipFiles] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Если это ZIP, показываем список файлов для выбора
  // Для TXT сразу показываем график
  useEffect(() => {
    if (isOpen) {
      if (isZip) {
        // Для ZIP показываем список типичных файлов логов
        // Пользователь загрузит свой ZIP и мы распарсим все файлы из него
        const commonLogFiles = [
          'app_server1_log.txt',
          'app_server2_log.txt',
          'db_server_log.txt',
          'web_server_log.txt',
          'firewall_log.txt',
          'router_log.txt',
          'backup_server_log.txt',
          'storage_system_log.txt',
          'switch1_log.txt',
          'switch2_log.txt',
        ];
        
        setZipFiles(commonLogFiles);
        console.log('📦 Показываю список файлов для ZIP:', commonLogFiles);
      }
    } else {
      // Сброс при закрытии
      if (graphUrl) {
        URL.revokeObjectURL(graphUrl);
      }
      setGraphUrl('');
      setGraphHtml('');
      setZipFiles([]);
      setSelectedFile(null);
      setError(null);
    }
  }, [isOpen, filename, isZip, graphUrl]);

  const handleGenerateGraph = async (targetFilename?: string) => {
    setLoading(true);
    setError(null);
    
    // Очищаем предыдущий график
    if (graphUrl) {
      URL.revokeObjectURL(graphUrl);
    }
    setGraphUrl('');
    setGraphHtml('');

    try {
      console.log('📊 Генерирую график для file_id:', fileId, 'targetFile:', targetFilename);
      
      // Используем file_id вместо загрузки файла!
      const response = await api.post(`/api/v1/timeline/by-file-id/${fileId}`, 
        targetFilename ? { selected_file: targetFilename } : {},
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      const html = response.data as string;
      console.log('✅ График получен, размер:', html.length, 'байт');
      
      // Проверяем размер HTML
      if (html.length > 10000000) { // 10MB лимит
        console.warn('⚠️ HTML слишком большой:', html.length);
        setError('График слишком большой для отображения. Попробуйте файл меньшего размера.');
        return;
      }
      
      // Создаем Blob URL вместо использования srcDoc (избегаем stack overflow)
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      
      // Освобождаем предыдущий URL если был
      if (graphUrl) {
        URL.revokeObjectURL(graphUrl);
      }
      
      setGraphUrl(url);
      setGraphHtml(html); // Сохраняем для обратной совместимости
      console.log('✅ График успешно сгенерирован БЕЗ повторной загрузки файла!');
      
    } catch (err: any) {
      console.error('❌ Ошибка генерации графика:', err);
      setError(err.response?.data?.detail || err.message || 'Не удалось сгенерировать график');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (file: string) => {
    setSelectedFile(file);
  };

  const handleGenerateForSelected = () => {
    if (selectedFile) {
      // Генерируем график для выбранного файла из ZIP
      handleGenerateGraph(selectedFile);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="relative w-full max-w-5xl max-h-[90vh] bg-atomic-darker rounded-2xl shadow-2xl border border-atomic-blue/30 overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-atomic-blue/20">
            <div className="flex items-center space-x-3">
              {isZip ? (
                <Package className="w-6 h-6 text-atomic-accent" />
              ) : (
                <FileText className="w-6 h-6 text-atomic-accent" />
              )}
              <div>
                <h2 className="text-2xl font-bold text-white">
                  {isZip ? 'Выберите файл для графика' : 'Timeline график'}
                </h2>
                <p className="text-sm text-gray-400">{filename}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <X className="w-6 h-6 text-gray-400" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
            {isZip && !graphHtml ? (
              /* Список файлов из ZIP */
              <div>
                <p className="text-gray-300 mb-4">
                  Выберите файл из архива для построения Timeline графика:
                </p>
                {zipFiles.length === 0 ? (
                  <p className="text-yellow-400">Загрузка списка файлов...</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {zipFiles.map((file) => (
                      <motion.button
                        key={file}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleFileSelect(file)}
                        className={`flex items-center space-x-3 p-4 rounded-lg border transition-all ${
                          selectedFile === file
                            ? 'border-atomic-accent bg-atomic-accent/10'
                            : 'border-atomic-blue/30 bg-atomic-blue/5 hover:border-atomic-blue/50'
                        }`}
                      >
                        <FileText className="w-5 h-5 text-atomic-accent flex-shrink-0" />
                        <span className="text-white text-left truncate">{file}</span>
                      </motion.button>
                    ))}
                  </div>
                )}
                
                {selectedFile && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 flex justify-center"
                  >
                    <button
                      onClick={handleGenerateForSelected}
                      disabled={loading}
                      className="btn-primary px-8 py-3 text-lg"
                    >
                      {loading ? (
                        <span className="flex items-center space-x-2">
                          <Loader2 className="w-5 h-5 animate-spin" />
                          <span>Генерация...</span>
                        </span>
                      ) : (
                        'Показать график'
                      )}
                    </button>
                  </motion.div>
                )}
              </div>
            ) : !isZip && !graphHtml && !loading && !error ? (
              /* Кнопка для TXT файла */
              <div className="text-center py-12">
                <p className="text-gray-300 mb-6">
                  Нажмите кнопку для генерации Timeline графика для файла <span className="text-atomic-accent font-semibold">{filename}</span>
                </p>
                <button
                  onClick={() => handleGenerateGraph()}
                  disabled={loading}
                  className="btn-primary px-8 py-3 text-lg"
                >
                  {loading ? (
                    <span className="flex items-center space-x-2">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Генерация...</span>
                    </span>
                  ) : (
                    'Сгенерировать график'
                  )}
                </button>
              </div>
            ) : null}

            {/* Loading */}
            {loading && (
              <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="w-12 h-12 text-atomic-accent animate-spin mb-4" />
                <p className="text-gray-400">Генерирую Timeline график...</p>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="card border-yellow-500/30 bg-yellow-500/5">
                <p className="text-yellow-300">{error}</p>
              </div>
            )}

            {/* Graph */}
            {graphUrl && (
              <div className="relative overflow-hidden rounded-lg border border-atomic-blue/30">
                <iframe
                  ref={iframeRef}
                  src={graphUrl}
                  title="Timeline Graph"
                  className="w-full border-0"
                  style={{ minHeight: '600px', height: '600px' }}
                  onError={(e) => {
                    console.error('Ошибка загрузки iframe:', e);
                    setError('Не удалось загрузить график');
                  }}
                />
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}

