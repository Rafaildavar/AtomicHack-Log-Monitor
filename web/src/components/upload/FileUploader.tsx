import { useCallback, useState } from 'react';
import { Upload, X, FileText, File } from 'lucide-react';
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
  const [dragActive, setDragActive] = useState<'logs' | 'anomalies' | null>(null);

  const handleDrag = useCallback((e: React.DragEvent, type: 'logs' | 'anomalies') => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(type);
    } else if (e.type === "dragleave") {
      setDragActive(null);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent, type: 'logs' | 'anomalies') => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(null);
    
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0], type);
    }
  }, [disabled, onFileSelect]);

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
            ${dragActive === type 
              ? 'border-atomic-accent bg-atomic-accent/10' 
              : 'border-gray-700 hover:border-atomic-blue bg-gray-800/30 hover:bg-gray-800/50'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
          onDragEnter={(e) => handleDrag(e, type)}
          onDragLeave={(e) => handleDrag(e, type)}
          onDragOver={(e) => handleDrag(e, type)}
          onDrop={(e) => handleDrop(e, type)}
        >
          <div className="flex flex-col items-center space-y-3 text-center">
            <div className={`p-3 rounded-full ${dragActive === type ? 'bg-atomic-accent/20' : 'bg-gray-700/50'}`}>
              <Upload className={`w-8 h-8 ${dragActive === type ? 'text-atomic-accent' : 'text-gray-400'}`} />
            </div>
            <div>
              <p className="text-lg font-semibold text-white">{title}</p>
              <p className="text-sm text-gray-400 mt-1">{description}</p>
            </div>
            <p className="text-xs text-gray-500">
              {type === 'logs' ? 'Поддерживается: .txt, .log, .zip (до 20MB)' : 'Поддерживается: .csv'}
            </p>
          </div>
        </label>
      ) : (
        <div className="p-6 border-2 border-atomic-blue/50 rounded-xl bg-gray-800/50">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <div className="p-2 rounded-lg bg-atomic-blue/20">
                {file.name.endsWith('.zip') ? (
                  <File className="w-6 h-6 text-atomic-accent" />
                ) : (
                  <FileText className="w-6 h-6 text-atomic-accent" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium truncate">{file.name}</p>
                <p className="text-sm text-gray-400">{formatFileSize(file.size)}</p>
              </div>
            </div>
            <button
              onClick={() => onFileRemove(type)}
              disabled={disabled}
              className="p-2 rounded-lg hover:bg-gray-700 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      <UploadZone
        type="logs"
        title="Загрузите файлы с логами"
        description="Перетащите файл сюда или нажмите для выбора"
        file={logFile}
      />

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-700"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-4 bg-atomic-dark text-gray-400">Опционально</span>
        </div>
      </div>

      <UploadZone
        type="anomalies"
        title="Словарь аномалий (опционально)"
        description="Если не указан, будет использован встроенный словарь"
        file={anomaliesFile}
      />

      {!anomaliesFile && (
        <div className="text-center">
          <p className="text-sm text-gray-500">
            💡 Без словаря будет использован встроенный словарь с 500+ аномалиями
          </p>
        </div>
      )}
    </div>
  );
}

