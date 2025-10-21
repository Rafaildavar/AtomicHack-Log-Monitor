import { Activity, AlertTriangle, FileText, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { formatNumber } from '../../lib/utils';

interface StatsCardsProps {
  totalProblems: number;
  uniqueAnomalies: number;
  uniqueProblems: number;
  uniqueFiles: number;
}

export default function StatsCards({
  totalProblems,
  uniqueAnomalies,
  uniqueProblems,
  uniqueFiles,
}: StatsCardsProps) {
  const stats = [
    {
      icon: AlertCircle,
      label: 'Всего проблем',
      value: totalProblems,
      color: 'text-red-400',
      bgColor: 'bg-red-400/10',
      borderColor: 'border-red-400/30',
    },
    {
      icon: AlertTriangle,
      label: 'Уникальных аномалий',
      value: uniqueAnomalies,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-400/10',
      borderColor: 'border-yellow-400/30',
    },
    {
      icon: Activity,
      label: 'Типов проблем',
      value: uniqueProblems,
      color: 'text-atomic-accent',
      bgColor: 'bg-atomic-accent/10',
      borderColor: 'border-atomic-accent/30',
    },
    {
      icon: FileText,
      label: 'Файлов с проблемами',
      value: uniqueFiles,
      color: 'text-purple-400',
      bgColor: 'bg-purple-400/10',
      borderColor: 'border-purple-400/30',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`card ${stat.bgColor} border ${stat.borderColor}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
                <p className={`text-3xl font-bold ${stat.color}`}>
                  {formatNumber(stat.value)}
                </p>
              </div>
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <Icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

