import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, AlertCircle } from 'lucide-react';

interface TimelineVisualizationProps {
  className?: string;
}

export default function TimelineVisualization({ className = '' }: TimelineVisualizationProps) {
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [loading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    // Пробуем загрузить график из sessionStorage (текущая сессия)
    const loadTimelineFromSession = () => {
      const sessionData = sessionStorage.getItem('analysis_results');
      if (sessionData) {
        try {
          const data = JSON.parse(sessionData);
          if (data.log_visualization) {
            setHtmlContent(data.log_visualization);
            return;
          }
        } catch (e) {
          console.error('Ошибка загрузки из sessionStorage:', e);
        }
      }

      // Если не нашли в sessionStorage, показываем информационное сообщение
      const saved = localStorage.getItem('analysis_history');
      if (!saved) {
        setError('Нет данных для отображения. Выполните анализ логов.');
        return;
      }

      try {
        const history = JSON.parse(saved);
        if (history.length === 0) {
          setError('История анализов пуста. Выполните анализ логов.');
          return;
        }

        // HTML графики не сохраняются в localStorage из-за ограничений памяти
        setError('Timeline графики доступны только на странице Results сразу после анализа. Выполните новый анализ, чтобы увидеть график.');
      } catch (e) {
        console.error('Ошибка загрузки Timeline:', e);
        setError('Ошибка загрузки данных из истории.');
      }
    };

    loadTimelineFromSession();
  }, []);

  // Автоматическая подстройка высоты iframe под содержимое
  useEffect(() => {
    if (iframeRef.current && htmlContent) {
      const iframe = iframeRef.current;
      
      const adjustHeight = () => {
        try {
          if (iframe.contentWindow) {
            const body = iframe.contentWindow.document.body;
            const html = iframe.contentWindow.document.documentElement;
            const height = Math.max(
              body?.scrollHeight || 0,
              html?.scrollHeight || 0,
              500 // минимальная высота
            );
            iframe.style.height = `${height}px`;
          }
        } catch (e) {
          // Игнорируем ошибки CORS при доступе к iframe
          console.log('Could not adjust iframe height:', e);
        }
      };

      iframe.onload = adjustHeight;
      adjustHeight();
    }
  }, [htmlContent]);

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`card flex items-center justify-center py-12 ${className}`}
      >
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="w-8 h-8 text-atomic-accent animate-spin" />
          <p className="text-gray-400">Загрузка Timeline графика...</p>
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`card border-yellow-500/30 bg-yellow-500/5 ${className}`}
      >
        <div className="flex items-start space-x-3 py-6">
          <AlertCircle className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-yellow-400 mb-2">
              Timeline недоступен
            </h3>
            <p className="text-yellow-300/80">{error}</p>
          </div>
        </div>
      </motion.div>
    );
  }

  if (!htmlContent || htmlContent.length < 100) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`card ${className}`}
      >
        <p className="text-gray-400 text-center py-8">
          График Timeline будет доступен после анализа логов
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className={`card ${className}`}
      style={{ 
        border: '1px solid rgba(0, 212, 255, 0.2)',
        background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(138, 43, 226, 0.05) 100%)'
      }}
    >
      <h3 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
        <span>📊</span>
        <span>Timeline с аномалиями</span>
      </h3>
      <div className="relative overflow-hidden rounded-lg">
        <iframe
          ref={iframeRef}
          srcDoc={htmlContent}
          title="Timeline Visualization"
          className="w-full border-0"
          style={{ minHeight: '500px' }}
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    </motion.div>
  );
}

