import { useMemo } from 'react';
import { motion } from 'framer-motion';

interface LogVisualizationProps {
  htmlContent?: string;
}

export default function LogVisualization({ htmlContent }: LogVisualizationProps) {
  if (!htmlContent || htmlContent.length < 100) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.35 }}
      className="card mb-8"
    >
      <h3 className="text-lg font-bold text-white mb-4">📊 Визуализация логов</h3>
      <div 
        className="w-full rounded-lg overflow-hidden bg-atomic-darker border border-atomic-blue/20"
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />
    </motion.div>
  );
}
