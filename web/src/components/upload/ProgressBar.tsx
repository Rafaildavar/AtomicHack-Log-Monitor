import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

interface ProgressBarProps {
  progress: number;
  status?: string;
}

export default function ProgressBar({ progress, status }: ProgressBarProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-4 h-4 text-atomic-accent animate-spin" />
          <span className="text-gray-300">{status || 'Анализ логов...'}</span>
        </div>
        <span className="text-atomic-accent font-semibold">{Math.round(progress)}%</span>
      </div>

      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-atomic-blue to-atomic-accent"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

