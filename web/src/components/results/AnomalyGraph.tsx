import { motion } from 'framer-motion';

interface AnomalyGraphProps {
  htmlContent?: string;
}

export default function AnomalyGraph({ htmlContent }: AnomalyGraphProps) {
  if (!htmlContent) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.36 }}
      className="card mb-8"
    >
      <h3 className="text-lg font-bold text-white mb-4">🔗 Граф связей аномалий</h3>
      <div 
        className="w-full rounded-lg overflow-hidden bg-atomic-darker"
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />
    </motion.div>
  );
}
