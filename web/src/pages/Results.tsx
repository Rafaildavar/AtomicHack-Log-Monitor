import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Download, ArrowLeft, FileText, AlertCircle } from 'lucide-react';
import StatsCards from '../components/results/StatsCards';
import type { AnalyzeResponse } from '../api/client';
import { api } from '../api/client';
import { downloadBlob } from '../lib/utils';
import LogVisualization from '../components/results/LogVisualization';
import AnomalyGraph from '../components/results/AnomalyGraph';

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const data = location.state?.data as AnalyzeResponse;
  const error = location.state?.error as string | null;

  // Если произошла ошибка
  if (error) {
    return (
      <div className="min-h-screen bg-atomic-dark flex items-center justify-center pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-2xl">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card border-red-500/50 bg-red-500/10"
          >
            <div className="flex items-start space-x-4">
              <AlertCircle className="w-8 h-8 text-red-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-red-400 mb-2">Ошибка анализа</h1>
                <p className="text-red-300/90 mb-6">{error}</p>
                <button
                  onClick={() => navigate('/analyze')}
                  className="btn-primary"
                >
                  Вернуться к анализу
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  // Если данные не переданы, перенаправляем на главную
  if (!data) {
    return (
      <div className="min-h-screen bg-atomic-dark flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-atomic-accent mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">Результаты не найдены</h1>
          <p className="text-gray-400 mb-4">Пожалуйста, выполните анализ заново</p>
          <button
            onClick={() => navigate('/analyze')}
            className="btn-primary"
          >
            Начать анализ
          </button>
        </div>
      </div>
    );
  }

  const handleDownloadExcel = async () => {
    if (data.excel_report) {
      try {
        console.log('📥 Скачивание Excel отчета:', data.excel_report);
        const response = await api.get(data.excel_report, { responseType: 'blob' });
        const filename = `analysis_report_${new Date().toISOString().split('T')[0]}.xlsx`;
        downloadBlob(response.data, filename);
        console.log('✅ Excel отчет скачан:', filename);
      } catch (error) {
        console.error('❌ Ошибка при скачивании Excel:', error);
        alert('Не удалось скачать отчет Excel. Попробуйте позже.');
      }
    }
  };

  return (
    <div className="min-h-screen bg-atomic-dark text-white pb-20">
      {/* Header */}
      <div className="bg-atomic-darker border-b border-atomic-blue/20 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/analyze')}
                className="btn-primary flex items-center space-x-2 hover:scale-105 transition-transform"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Новый анализ</span>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-atomic-accent">Результаты анализа</h1>
                <p className="text-gray-400">Детальный отчет по обнаруженным аномалиям</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleDownloadExcel}
                className="btn-secondary flex items-center space-x-2"
                disabled={!data.excel_report}
              >
                <Download className="w-4 h-4" />
                <span>Скачать Excel</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Статистика */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-xl font-bold text-white mb-4">Общая статистика</h2>
          <StatsCards
            totalProblems={data.analysis.ml_results.total_problems}
            uniqueAnomalies={data.analysis.ml_results.unique_anomalies}
            uniqueProblems={data.analysis.ml_results.unique_problems}
            uniqueFiles={data.analysis.ml_results.unique_files}
          />
        </motion.div>

        {/* Детальная статистика */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Распределение по уровням */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <h3 className="text-lg font-bold text-white mb-4">Распределение по уровням</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Всего строк</span>
                <span className="text-white font-semibold">{data.analysis.basic_stats.total_lines}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-red-400">Ошибки (ERROR)</span>
                <span className="text-red-400 font-semibold">{data.analysis.basic_stats.error_count}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-yellow-400">Предупреждения (WARN)</span>
                <span className="text-yellow-400 font-semibold">{data.analysis.basic_stats.warning_count}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-green-400">Информация (INFO)</span>
                <span className="text-green-400 font-semibold">{data.analysis.basic_stats.info_count}</span>
              </div>
            </div>
          </motion.div>

          {/* Настройки анализа */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <h3 className="text-lg font-bold text-white mb-4">Параметры анализа</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Порог схожести</span>
                <span className="text-atomic-accent font-semibold">{data.analysis.threshold_used}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Статус</span>
                <span className="text-green-400 font-semibold">{data.status}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Уверенность ML</span>
                <span className="text-atomic-accent font-semibold">90%</span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* График логов */}
        <LogVisualization htmlContent={data.log_visualization} />

        {/* Граф аномалий */}
        <AnomalyGraph htmlContent={data.anomaly_graph} />

        {/* Список аномалий */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-white">Обнаруженные аномалии</h3>
            <span className="text-sm text-gray-400">
              Найдено: {data.results.length} проблем
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-atomic-blue/20">
                  <th className="text-left py-3 px-4 text-gray-400">ID</th>
                  <th className="text-left py-3 px-4 text-gray-400">Файл</th>
                  <th className="text-left py-3 px-4 text-gray-400">Строка</th>
                  <th className="text-left py-3 px-4 text-gray-400">Содержание</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((result, index) => (
                  <motion.tr
                    key={result['ID аномалии']}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="border-b border-atomic-blue/10 hover:bg-atomic-blue/5"
                  >
                    <td className="py-3 px-4 text-atomic-accent font-semibold">
                      {result['ID аномалии']}
                    </td>
                    <td className="py-3 px-4 text-gray-300">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-atomic-blue" />
                        <span className="truncate max-w-xs">
                          {result['Файл с проблемой']}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-300">
                      {result['№ строки']}
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-gray-300 max-w-md truncate">
                        {result['Строка из лога']}
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.results.length === 0 && (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
              <p className="text-gray-400">Аномалии не обнаружены! Логи выглядят корректно.</p>
            </div>
          )}
        </motion.div>

        {/* Рекомендации */}
        {data.results.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-6 card border-yellow-400/20 bg-yellow-400/5"
          >
            <h3 className="text-lg font-bold text-yellow-400 mb-3">Рекомендации</h3>
            <ul className="space-y-2 text-gray-300">
              <li className="flex items-start space-x-2">
                <span className="w-1.5 h-1.5 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></span>
                <span>Проверьте настройки аутентификации - обнаружены ошибки входа</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="w-1.5 h-1.5 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></span>
                <span>Мониторьте использование памяти - зафиксированы предупреждения</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="w-1.5 h-1.5 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></span>
                <span>Проверьте подключение к внешним сервисам</span>
              </li>
            </ul>
          </motion.div>
        )}
      </div>
    </div>
  );
}
