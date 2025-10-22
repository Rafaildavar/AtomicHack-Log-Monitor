import { Upload, X, FileText } from 'lucide-react';
import { formatFileSize } from '../../lib/utils';

interface FileUploaderProps {
  onFileSelect: (file: File, type: 'logs' | 'anomalies') => void;
  onFileRemove: (type: 'logs' | 'anomalies') => void;
  logFile: File | null;
  anomaliesFile: File | null;
  disabled?: boolean;
}

export default function FileUploader({
  onFileSelect,
  onFileRemove,
  logFile,
  anomaliesFile,
  disabled = false,
}: FileUploaderProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'logs' | 'anomalies') => {
    if (disabled) return;
    
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0], type);
    }
  };

  const UploadZone = ({ 
    type, 
    title, 
    description, 
    file 
  }: { 
    type: 'logs' | 'anomalies', 
    title: string, 
    description: string,
    file: File | null 
  }) => (
    <div className="relative">
      <input
        id={`file-upload-${type}`}
        type="file"
        className="hidden"
        accept={type === 'logs' ? '.txt,.log,.zip' : '.csv'}
        onChange={(e) => handleChange(e, type)}
        disabled={disabled}
      />
      
      {!file ? (
        <label
          htmlFor={`file-upload-${type}`}
          className={`
            block p-8 border-2 border-dashed rounded-xl cursor-pointer transition-all
            ${type === 'logs' 
              ? 'border-atomic-accent bg-atomic-accent/10' 
              : 'border-gray-700 hover:border-atomic-blue bg-gray-800/30 hover:bg-gray-800/50'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <div className="flex flex-col items-center">
            <Upload className="w-8 h-8 text-gray-400 mb-2" />
            <p className="text-sm font-medium text-white">{title}</p>
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          </div>
        </label>
      ) : (
        <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-xl flex items-start space-x-3">
          <FileText className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
          <div className="flex-1">
            <p className="text-sm font-medium text-white">{file.name}</p>
            <p className="text-xs text-gray-400 mt-1">{formatFileSize(file.size)}</p>
          </div>
          <button
            onClick={() => onFileRemove(type)}
            className="p-1 hover:bg-red-500/20 rounded transition-colors"
            disabled={disabled}
          >
            <X className="w-5 h-5 text-gray-400 hover:text-red-400" />
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-4 no-animation">
      <UploadZone 
        type="logs"
        title="Загрузите логи"
        description="файлы .txt, .log или .zip"
        file={logFile}
      />
      <UploadZone 
        type="anomalies"
        title="Словарь аномалий (опционально)"
        description="файл .csv"
        file={anomaliesFile}
      />
    </div>
  );
}

