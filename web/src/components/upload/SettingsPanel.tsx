import { Settings } from 'lucide-react';

interface SettingsPanelProps {
  threshold: number;
  onThresholdChange: (value: number) => void;
  disabled?: boolean;
}

export default function SettingsPanel({
  threshold,
  onThresholdChange,
  disabled = false
}: SettingsPanelProps) {
  return (
    <div className="card no-animation">
      <div className="flex items-center space-x-2 mb-4">
        <Settings className="w-5 h-5 text-atomic-accent" />
        <h3 className="text-lg font-semibold text-white">Настройки анализа</h3>
      </div>

      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-300">
              Порог similarity (threshold)
            </label>
            <span className="text-sm font-mono text-atomic-accent">
              {threshold.toFixed(2)}
            </span>
          </div>
          
          <input
            type="range"
            min="0.5"
            max="1.0"
            step="0.05"
            value={threshold}
            onChange={(e) => onThresholdChange(parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-atomic-blue disabled:opacity-50"
          />
          
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0.5 (мягкий)</span>
            <span>0.7 (рекомендуемый)</span>
            <span>1.0 (строгий)</span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700/50">
          <p className="text-xs text-gray-400">
            <span className="font-semibold text-gray-300">Что это?</span>
            <br />
            Порог определяет насколько похожей должна быть аномалия на известные из словаря.
            <br />
            • <span className="text-atomic-accent">0.7</span> - оптимальный баланс
            <br />
            • <span className="text-atomic-accent">0.5-0.65</span> - больше новых аномалий
            <br />
            • <span className="text-atomic-accent">0.75-1.0</span> - только точные совпадения
          </p>
        </div>
      </div>
    </div>
  );
}

