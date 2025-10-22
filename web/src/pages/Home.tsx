import { Link } from 'react-router-dom';
import { Activity, Zap, Shield, Database, ArrowRight, FileText, BarChart3, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section - Professional */}
      <section className="relative pt-32 pb-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center space-y-6"
          >
            <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-atomic-blue/20 border border-atomic-blue/30">
              <Activity className="w-4 h-4 text-atomic-accent" />
              <span className="text-sm text-gray-300">AtomicHack Log Monitor</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight">
              Система мониторинга и анализа
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-atomic-blue to-atomic-accent">
                журналов событий
              </span>
            </h1>

            <p className="text-lg text-gray-400 max-w-3xl mx-auto">
              Интеллектуальная система на базе ML для автоматического выявления аномалий 
              и критических проблем в логах корпоративных систем
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link to="/analyze" className="btn-primary text-lg px-8 py-4">
                Начать анализ
                <ArrowRight className="w-5 h-5 ml-2 inline" />
              </Link>
              <Link to="/docs" className="btn-secondary text-lg px-8 py-4">
                Документация API
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Key Features */}
      <section className="py-16 px-4 bg-gradient-to-b from-transparent to-atomic-darker">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ключевые возможности
            </h2>
            <p className="text-lg text-gray-400">
              Комплексное решение для мониторинга критической инфраструктуры
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card"
            >
              <div className="w-12 h-12 rounded-lg bg-atomic-blue/20 flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-atomic-accent" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">ML-анализ в реальном времени</h3>
              <p className="text-gray-400">
                Автоматическое обнаружение аномалий с использованием Sentence Transformers и semantic search
              </p>
            </motion.div>

            {/* Feature 2 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card"
            >
              <div className="w-12 h-12 rounded-lg bg-atomic-blue/20 flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-atomic-accent" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Высокая точность обнаружения</h3>
              <p className="text-gray-400">
                Настраиваемый порог similarity для баланса между точностью и полнотой обнаружения
              </p>
            </motion.div>

            {/* Feature 3 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card"
            >
              <div className="w-12 h-12 rounded-lg bg-atomic-blue/20 flex items-center justify-center mb-4">
                <Database className="w-6 h-6 text-atomic-accent" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">REST API для интеграции</h3>
              <p className="text-gray-400">
                Готовое API для интеграции с существующими системами мониторинга и SIEM
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Процесс работы
            </h2>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {[
              { icon: FileText, title: 'Загрузка логов', desc: 'Поддержка .txt, .log, .zip' },
              { icon: Activity, title: 'ML-обработка', desc: 'Анализ через Sentence Transformers' },
              { icon: BarChart3, title: 'Выявление аномалий', desc: 'Сопоставление с базой проблем' },
              { icon: Clock, title: 'Генерация отчета', desc: 'Excel с детальной трассировкой' },
            ].map((step, idx) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="card text-center relative"
              >
                {idx < 3 && (
                  <div className="hidden md:block absolute top-1/2 -right-3 w-6 h-0.5 bg-gradient-to-r from-atomic-blue to-transparent"></div>
                )}
                <div className="w-16 h-16 rounded-full bg-atomic-blue/20 flex items-center justify-center mx-auto mb-4">
                  <step.icon className="w-8 h-8 text-atomic-accent" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-gray-400">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Details */}
      <section className="py-16 px-4 bg-gradient-to-b from-atomic-darker to-transparent">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-3xl md:text-4xl font-bold text-white">
                Технические характеристики
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-atomic-accent mt-2"></div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Масштабируемость</h3>
                    <p className="text-gray-400">Обработка больших объемов логов с поддержкой пакетной загрузки</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-atomic-accent mt-2"></div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Производительность</h3>
                    <p className="text-gray-400">Анализ логов за секунды благодаря оптимизированной ML-модели</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-atomic-accent mt-2"></div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Интеграция</h3>
                    <p className="text-gray-400">Docker deployment, REST API, Telegram bot</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-atomic-accent mt-2"></div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Настраиваемость</h3>
                    <p className="text-gray-400">Собственные словари аномалий и настройка порога чувствительности</p>
                  </div>
                </div>
              </div>

              <div className="pt-4">
                <Link to="/analyze" className="btn-primary inline-flex items-center">
                  Перейти к анализу
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-6">
              <div className="card bg-atomic-blue/10 border-atomic-blue/30">
                <div className="text-4xl font-bold text-white mb-2">500+</div>
                <div className="text-sm text-gray-400">Типов аномалий в базе</div>
              </div>
              <div className="card bg-atomic-blue/10 border-atomic-blue/30">
                <div className="text-4xl font-bold text-white mb-2">90%</div>
                <div className="text-sm text-gray-400">Точность анализа</div>
              </div>
              <div className="card bg-atomic-blue/10 border-atomic-blue/30">
                <div className="text-4xl font-bold text-white mb-2">&lt;5 сек</div>
                <div className="text-sm text-gray-400">Время обработки</div>
              </div>
              <div className="card bg-atomic-blue/10 border-atomic-blue/30">
                <div className="text-4xl font-bold text-white mb-2">24/7</div>
                <div className="text-sm text-gray-400">Мониторинг</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="card text-center space-y-6 bg-gradient-to-r from-atomic-blue/20 to-atomic-accent/20 border-atomic-blue/30">
            <h2 className="text-3xl md:text-4xl font-bold text-white">
              Начните работу с системой
            </h2>
            <p className="text-xl text-gray-300">
              Загрузите логи и получите детальный анализ аномалий
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/analyze" className="btn-primary text-lg px-8 py-4">
                Анализировать логи
              </Link>
              <a 
                href="https://t.me/AtomicHackLogBot" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="btn-secondary text-lg px-8 py-4"
              >
                Telegram Bot
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
