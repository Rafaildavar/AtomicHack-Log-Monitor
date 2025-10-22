import { motion } from 'framer-motion';
import { Code, Terminal, ExternalLink, Copy, Check } from 'lucide-react';
import { useState } from 'react';

export default function Documentation() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const copyToClipboard = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const CodeBlock = ({ code, language = 'bash', title, id }: { code: string; language?: string; title: string; id: string }) => (
    <div className="card mb-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-mono text-gray-400">{language}</span>
        <button
          onClick={() => copyToClipboard(code, id)}
          className="text-gray-400 hover:text-atomic-accent transition-colors"
          title="Copy code"
        >
          {copiedCode === id ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      </div>
      <pre className="bg-atomic-darker/50 rounded p-3 overflow-x-auto text-sm text-gray-300">
        <code>{code}</code>
      </pre>
    </div>
  );

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto max-w-4xl">
        {/* Header */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            API Документация
          </h1>
          <p className="text-xl text-gray-400">
            Полное описание REST API для интеграции системы анализа логов
          </p>
        </motion.section>

        {/* Base URL */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="card">
            <h2 className="text-2xl font-bold text-white mb-4">Базовая информация</h2>
            <div className="space-y-3 text-gray-300">
              <div>
                <p className="text-gray-400 text-sm">Base URL</p>
                <p className="font-mono text-atomic-accent">http://localhost:8001/api/v1</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Версия API</p>
                <p className="font-mono">1.0.0</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Документация</p>
                <a 
                  href="http://localhost:8001/docs" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-atomic-accent hover:text-atomic-blue flex items-center gap-1"
                >
                  Swagger UI <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Endpoints */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold text-white mb-6">Эндпоинты</h2>

          {/* Analyze Endpoint */}
          <div className="space-y-4">
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <span className="px-3 py-1 rounded font-mono text-sm bg-green-500/20 text-green-400">POST</span>
                <span className="font-mono text-atomic-accent">/analyze</span>
              </div>
              <p className="text-gray-300 mb-4">Загрузить и проанализировать логи</p>
              
              <div className="bg-atomic-darker/50 rounded p-4 mb-4">
                <p className="text-sm font-semibold text-white mb-3">Request</p>
                <div className="space-y-2 text-sm">
                  <div>
                    <p className="text-gray-400">Content-Type: multipart/form-data</p>
                  </div>
                  <div className="mt-3">
                    <p className="text-gray-300 font-mono">Parameters:</p>
                    <ul className="mt-2 space-y-1 text-gray-400">
                      <li>• <span className="text-atomic-accent">log_file</span> (File, required) - файл с логами</li>
                      <li>• <span className="text-atomic-accent">anomalies_file</span> (File, optional) - CSV словарь</li>
                      <li>• <span className="text-atomic-accent">threshold</span> (string, default: "0.7") - порог схожести</li>
                    </ul>
                  </div>
                </div>
              </div>

              <CodeBlock
                id="curl-analyze"
                title="cURL"
                language="bash"
                code={`curl -X POST "http://localhost:8001/api/v1/analyze" \\
  -F "log_file=@logs.txt" \\
  -F "threshold=0.7"`}
              />

              <CodeBlock
                id="python-analyze"
                title="Python"
                language="python"
                code={`import requests

with open('logs.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/v1/analyze',
        files={'log_file': f},
        data={'threshold': '0.7'}
    )

result = response.json()
print(result)`}
              />

              <CodeBlock
                id="js-analyze"
                title="JavaScript"
                language="javascript"
                code={`const formData = new FormData();
formData.append('log_file', fileInput.files[0]);
formData.append('threshold', '0.7');

const response = await fetch('http://localhost:8001/api/v1/analyze', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);`}
              />
            </div>

            {/* Response Example */}
            <div className="card">
              <p className="text-sm font-semibold text-white mb-3">Response (200 OK)</p>
              <CodeBlock
                id="response-analyze"
                title="JSON"
                language="json"
                code={`{
  "status": "success",
  "analysis": {
    "basic_stats": {
      "total_lines": 1500,
      "error_count": 45,
      "warning_count": 120
    },
    "ml_results": {
      "total_problems": 23,
      "unique_anomalies": 15,
      "unique_problems": 18,
      "unique_files": 5
    },
    "threshold_used": 0.7
  },
  "results": [
    {
      "ID аномалии": 1,
      "ID проблемы": 5,
      "Файл с проблемой": "app_server1_log.txt",
      "№ строки": 123,
      "Строка из лога": "ERROR: Connection timeout"
    }
  ],
  "excel_report": "/api/v1/download/analysis_report_2025-10-22.xlsx"
}`}
              />
            </div>
          </div>
        </motion.section>

        {/* Download Endpoint */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <span className="px-3 py-1 rounded font-mono text-sm bg-blue-500/20 text-blue-400">GET</span>
              <span className="font-mono text-atomic-accent">/download/{'{filename}'}</span>
            </div>
            <p className="text-gray-300 mb-4">Скачать сгенерированный Excel отчет</p>
            
            <CodeBlock
              id="curl-download"
              title="cURL"
              language="bash"
              code={`curl -X GET "http://localhost:8001/api/v1/download/analysis_report.xlsx" \\
  -o report.xlsx`}
            />

            <div className="bg-atomic-darker/50 rounded p-4">
              <p className="text-sm text-gray-400">Returns: .xlsx файл (Excel отчет)</p>
            </div>
          </div>
        </motion.section>

        {/* Implementation Guide */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold text-white mb-6">Руководство по интеграции</h2>

          <div className="space-y-6">
            {/* Step 1 */}
            <div className="card">
              <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
                <span className="w-8 h-8 rounded-full bg-atomic-blue/20 flex items-center justify-center text-sm font-bold">1</span>
                Подготовка файла логов
              </h3>
              <p className="text-gray-300 mb-3">Поддерживаются форматы:</p>
              <ul className="space-y-1 text-gray-400 text-sm">
                <li>• <span className="text-atomic-accent">.txt</span> - текстовый файл с логами</li>
                <li>• <span className="text-atomic-accent">.log</span> - логи в стандартном формате</li>
                <li>• <span className="text-atomic-accent">.zip</span> - архив с логами и словарём аномалий</li>
              </ul>
            </div>

            {/* Step 2 */}
            <div className="card">
              <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
                <span className="w-8 h-8 rounded-full bg-atomic-blue/20 flex items-center justify-center text-sm font-bold">2</span>
                Отправка запроса
              </h3>
              <CodeBlock
                id="integration-step2"
                language="javascript"
                title="Пример интеграции"
                code={`async function analyzeLogs(file, threshold = 0.7) {
  const formData = new FormData();
  formData.append('log_file', file);
  formData.append('threshold', threshold.toString());

  const response = await fetch('http://api-server:8001/api/v1/analyze', {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error('Analysis failed');
  }

  return await response.json();
}`}
              />
            </div>

            {/* Step 3 */}
            <div className="card">
              <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
                <span className="w-8 h-8 rounded-full bg-atomic-blue/20 flex items-center justify-center text-sm font-bold">3</span>
                Обработка результатов
              </h3>
              <CodeBlock
                id="integration-step3"
                language="javascript"
                title="Обработка ответа"
                code={`const result = await analyzeLogs(file);

// Проверка успеха
if (result.status === 'success') {
  const stats = result.analysis.ml_results;
  console.log(\`Найдено проблем: \${stats.total_problems}\`);
  console.log(\`Точность: 90%\`);

  // Скачивание Excel
  const excelUrl = result.excel_report;
  const excelResponse = await fetch(excelUrl);
  const blob = await excelResponse.blob();
  
  // Сохранение файла
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'report.xlsx';
  a.click();
}`}
              />
            </div>
          </div>
        </motion.section>

        {/* Error Handling */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold text-white mb-6">Обработка ошибок</h2>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                code: '400',
                title: 'Bad Request',
                desc: 'Неверные параметры или формат файла'
              },
              {
                code: '404',
                title: 'Not Found',
                desc: 'Файл отчета не найден'
              },
              {
                code: '500',
                title: 'Internal Error',
                desc: 'Ошибка на сервере при анализе'
              },
              {
                code: '503',
                title: 'Service Unavailable',
                desc: 'API временно недоступен'
              }
            ].map((error, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="card"
              >
                <div className="text-4xl font-bold text-red-400 mb-2">{error.code}</div>
                <h3 className="text-lg font-bold text-white mb-1">{error.title}</h3>
                <p className="text-gray-400 text-sm">{error.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Parameters Guide */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold text-white mb-6">Параметры анализа</h2>

          <div className="card">
            <h3 className="text-xl font-bold text-white mb-4">Threshold (Порог схожести)</h3>
            <div className="space-y-3">
              <p className="text-gray-300">
                Определяет, насколько похожей должна быть строка лога на известные аномалии из словаря.
              </p>
              <div className="bg-atomic-darker/50 rounded p-4">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">0.5 - 0.65</span>
                    <span className="text-gray-300">Мягкий (больше ложных срабатываний)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-atomic-accent font-semibold">0.7 (по умолчанию)</span>
                    <span className="text-gray-300">Оптимальный баланс</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">0.75 - 1.0</span>
                    <span className="text-gray-300">Строгий (только точные совпадения)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Best Practices */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold text-white mb-6">Рекомендации</h2>

          <div className="space-y-4">
            {[
              'Используйте порог 0.7 для общего случая',
              'Для больших файлов (>100MB) используйте асинхронную обработку',
              'Всегда проверяйте поле status в ответе перед использованием результатов',
              'Кэшируйте результаты анализа для одинаковых файлов',
              'Используйте свой словарь аномалий для специфических систем'
            ].map((tip, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="card flex items-start gap-3"
              >
                <span className="text-atomic-accent mt-1">✓</span>
                <p className="text-gray-300">{tip}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Support */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="text-center card bg-gradient-to-r from-atomic-blue/20 to-atomic-accent/20"
        >
          <Code className="w-12 h-12 text-atomic-accent mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-3">Нужна помощь?</h2>
          <p className="text-gray-300 mb-4">
            Полная документация и примеры доступны в интерактивном Swagger UI
          </p>
          <a
            href="http://localhost:8001/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-flex items-center gap-2"
          >
            Открыть Swagger UI
            <ExternalLink className="w-4 h-4" />
          </a>
        </motion.section>
      </div>
    </div>
  );
}
