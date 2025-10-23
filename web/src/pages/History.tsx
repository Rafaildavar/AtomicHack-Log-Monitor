import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Trash2, ExternalLink, Clock, FileText, AlertCircle, TrendingUp } from 'lucide-react';
import { formatDate, formatNumber } from '../lib/utils';
import type { AnalyzeResponse } from '../api/client';

interface HistoryItem {
  id: string;
  timestamp: string;
  filename: string;
  data: AnalyzeResponse;
}

export default function History() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Загружаем историю из localStorage
    const saved = localStorage.getItem('analysis_history');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setHistory(parsed);
      } catch (e) {
        console.error('Ошибка при загрузке истории:', e);
      }
    }
  }, []);

  const handleDelete = (id: string) => {
    const updated = history.filter(item => item.id !== id);
    setHistory(updated);
    localStorage.setItem('analysis_history', JSON.stringify(updated));
  };

  const handleClearAll = () => {
    if (window.confirm('Очистить всю историю анализов?')) {
      setHistory([]);
      localStorage.removeItem('analysis_history');
    }
  };

  const handleViewResults = (item: HistoryItem) => {
    navigate('/results', { state: { data: item.data, error: null } });
  };

  // Рассчитываем статистику
  const totalAnalyses = history.length;
  const totalProblems = history.reduce((sum, item) => sum + (item.data?.results?.length || 0), 0);
  const avgProblems = totalAnalyses > 0 ? (totalProblems / totalAnalyses).toFixed(1) : 0;

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            История анализов
          </h1>
          <p className="text-lg text-gray-400">
            Все ваши предыдущие анализы сохранены локально
          </p>
        </motion.div>

        {/* Stats Cards - только если есть история */}
        {history.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm mb-2">Всего анализов</p>
                  <p className="text-3xl font-bold text-white">{totalAnalyses}</p>
                </div>
                <FileText className="w-12 h-12 text-atomic-accent opacity-50" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm mb-2">Всего проблем найдено</p>
                  <p className="text-3xl font-bold text-red-400">{totalProblems}</p>
                </div>
                <AlertCircle className="w-12 h-12 text-red-400 opacity-50" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm mb-2">Среднее проблем на анализ</p>
                  <p className="text-3xl font-bold text-atomic-accent">{avgProblems}</p>
                </div>
                <TrendingUp className="w-12 h-12 text-atomic-accent opacity-50" />
              </div>
            </motion.div>
          </div>
        )}

        {history.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card text-center py-12"
          >
            <Clock className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-400 mb-2">
              История пуста
            </h2>
            <p className="text-gray-500 mb-6">
              Выполните анализ логов, чтобы увидеть результаты здесь
            </p>
            <button
              onClick={() => navigate('/analyze')}
              className="btn-primary"
            >
              Начать анализ
            </button>
          </motion.div>
        ) : (
          <>
            {/* Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 flex gap-4 justify-between items-center"
            >
              <div className="text-gray-400">
                Всего анализов: <span className="text-atomic-accent font-bold">{history.length}</span>
              </div>
              <button
                onClick={handleClearAll}
                className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/50 transition-colors text-sm font-medium"
              >
                Очистить всё
              </button>
            </motion.div>

            {/* History List */}
            <div className="space-y-4">
              {history.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="card hover:border-atomic-blue/50 transition-all group"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    {/* Left: Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <FileText className="w-5 h-5 text-atomic-accent flex-shrink-0" />
                        <h3 className="text-lg font-semibold text-white truncate">
                          {item.filename}
                        </h3>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Время</p>
                          <p className="text-gray-300">
                            {formatDate(item.timestamp)}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">Проблем</p>
                          <p className="text-atomic-accent font-bold">
                            {formatNumber(item.data?.analysis?.ml_results?.total_problems || 0)}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">Аномалий</p>
                          <p className="text-yellow-400 font-bold">
                            {formatNumber(item.data?.analysis?.ml_results?.unique_anomalies || 0)}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">Файлов</p>
                          <p className="text-purple-400 font-bold">
                            {formatNumber(item.data?.analysis?.ml_results?.unique_files || 0)}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex gap-2 flex-shrink-0">
                      <button
                        onClick={() => handleViewResults(item)}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-atomic-blue/20 hover:bg-atomic-blue/30 text-atomic-accent border border-atomic-blue/50 transition-all hover:scale-105"
                        title="Посмотреть результаты"
                      >
                        <ExternalLink className="w-4 h-4" />
                        <span className="hidden sm:inline">Просмотр</span>
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/50 transition-all hover:scale-105"
                        title="Удалить из истории"
                      >
                        <Trash2 className="w-4 h-4" />
                        <span className="hidden sm:inline">Удалить</span>
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
