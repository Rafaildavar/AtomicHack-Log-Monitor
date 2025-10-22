import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, AlertCircle, FileText } from 'lucide-react';

export default function Dashboard() {
  const [analysisHistory, setAnalysisHistory] = useState<any[]>([]);

  useEffect(() => {
    // Загружаем историю анализов из localStorage
    const saved = localStorage.getItem('analysis_history');
    if (saved) {
      try {
        const history = JSON.parse(saved);
        setAnalysisHistory(history);
      } catch (e) {
        console.error('Ошибка при загрузке истории:', e);
      }
    }
  }, []);

  // Рассчитываем статистику
  const totalAnalyses = analysisHistory.length;
  const totalProblems = analysisHistory.reduce((sum, item) => sum + (item.data?.results?.length || 0), 0);
  const avgProblems = totalAnalyses > 0 ? (totalProblems / totalAnalyses).toFixed(1) : 0;

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">📊 Dashboard</h1>
          <p className="text-gray-400">Статистика анализов и проблем</p>
        </motion.div>

        {/* Stats Cards */}
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

        {/* История анализов */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center space-x-2">
            <BarChart3 className="w-6 h-6" />
            <span>История анализов</span>
          </h2>

          {analysisHistory.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 mb-4">Анализы отсутствуют</p>
              <p className="text-sm text-gray-500">Начните анализ файлов логов, чтобы увидеть результаты здесь</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-atomic-blue/20">
                    <th className="text-left py-3 px-4 text-gray-400">Файл</th>
                    <th className="text-left py-3 px-4 text-gray-400">Время</th>
                    <th className="text-right py-3 px-4 text-gray-400">Проблем</th>
                    <th className="text-right py-3 px-4 text-gray-400">Аномалий</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisHistory.map((item, index) => (
                    <motion.tr
                      key={item.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.05 * index }}
                      className="border-b border-atomic-blue/10 hover:bg-atomic-blue/5"
                    >
                      <td className="py-3 px-4 text-gray-300">{item.filename}</td>
                      <td className="py-3 px-4 text-gray-300">
                        {new Date(item.timestamp).toLocaleString('ru-RU')}
                      </td>
                      <td className="py-3 px-4 text-right text-red-400 font-semibold">
                        {item.data?.results?.length || 0}
                      </td>
                      <td className="py-3 px-4 text-right text-atomic-accent font-semibold">
                        {item.data?.analysis?.ml_results?.unique_anomalies || 0}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>

        {/* Последний анализ с деталями */}
        {analysisHistory.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-8"
          >
            <h2 className="text-2xl font-bold text-white mb-6">📈 Последний анализ</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Детали последнего анализа */}
              <motion.div className="card">
                <h3 className="text-lg font-bold text-white mb-4">Информация</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Файл:</span>
                    <span className="text-white font-semibold">{analysisHistory[0].filename}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Время:</span>
                    <span className="text-white font-semibold">
                      {new Date(analysisHistory[0].timestamp).toLocaleString('ru-RU')}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Проблем найдено:</span>
                    <span className="text-red-400 font-semibold text-lg">
                      {analysisHistory[0].data?.results?.length || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Уникальных аномалий:</span>
                    <span className="text-atomic-accent font-semibold text-lg">
                      {analysisHistory[0].data?.analysis?.ml_results?.unique_anomalies || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Порог схожести:</span>
                    <span className="text-white font-semibold">
                      {analysisHistory[0].data?.analysis?.threshold_used || 0.7}
                    </span>
                  </div>
                </div>
              </motion.div>

              {/* Базовая статистика последнего анализа */}
              <motion.div className="card">
                <h3 className="text-lg font-bold text-white mb-4">Статистика</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Всего строк:</span>
                    <span className="text-white font-semibold">
                      {analysisHistory[0].data?.analysis?.basic_stats?.total_lines || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-red-400">ERROR:</span>
                    <span className="text-red-400 font-semibold">
                      {analysisHistory[0].data?.analysis?.basic_stats?.error_count || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-yellow-400">WARNING:</span>
                    <span className="text-yellow-400 font-semibold">
                      {analysisHistory[0].data?.analysis?.basic_stats?.warning_count || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-400">INFO:</span>
                    <span className="text-green-400 font-semibold">
                      {analysisHistory[0].data?.analysis?.basic_stats?.info_count || 0}
                    </span>
                  </div>
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
