import { Link } from 'react-router-dom';
import { Activity, Zap, Shield, TrendingUp, CheckCircle, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-atomic-blue/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-atomic-accent/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>

        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center space-y-8"
          >
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-atomic-blue/20 border border-atomic-blue/30">
              <Activity className="w-4 h-4 text-atomic-accent" />
              <span className="text-sm text-gray-300">AI-powered Log Analysis</span>
            </div>

            {/* Title */}
            <h1 className="text-5xl md:text-7xl font-bold text-white leading-tight">
              Анализ логов
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-atomic-blue to-atomic-accent">
                за секунды, не часы
              </span>
            </h1>

            {/* Description */}
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              ИИ-анализатор автоматически выявляет аномалии и критические проблемы в логах 
              с использованием ML semantic search
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/analyze" className="btn-primary text-lg px-8 py-4">
                Попробовать бесплатно
                <ArrowRight className="w-5 h-5 ml-2 inline" />
              </Link>
              <a 
                href="#demo" 
                className="btn-secondary text-lg px-8 py-4"
              >
                Посмотреть демо
              </a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto pt-12">
              <div>
                <div className="text-4xl font-bold text-white">4-е</div>
                <div className="text-sm text-gray-400 mt-1">место на хакатоне</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-white">99%</div>
                <div className="text-sm text-gray-400 mt-1">точность анализа</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-white">&lt;3 сек</div>
                <div className="text-sm text-gray-400 mt-1">скорость обработки</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-transparent to-atomic-darker">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
              Как это работает
            </h2>
            <p className="text-xl text-gray-400">
              Три простых шага до результата
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card text-center"
            >
              <div className="w-16 h-16 rounded-full bg-atomic-blue/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-atomic-accent">1</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Загрузите логи</h3>
              <p className="text-gray-400">
                Drag & drop файлов .txt, .log или .zip архивов до 20MB
              </p>
            </motion.div>

            {/* Step 2 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card text-center"
            >
              <div className="w-16 h-16 rounded-full bg-atomic-blue/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-atomic-accent">2</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">ML анализ</h3>
              <p className="text-gray-400">
                Sentence Transformers находят аномалии и связывают их с проблемами
              </p>
            </motion.div>

            {/* Step 3 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card text-center"
            >
              <div className="w-16 h-16 rounded-full bg-atomic-blue/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-atomic-accent">3</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Получите отчет</h3>
              <p className="text-gray-400">
                Excel отчет с детальной трассировкой аномалий и графики
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-3xl md:text-4xl font-bold text-white">
                Почему выбирают нас
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <Zap className="w-6 h-6 text-atomic-accent flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">Молниеносно быстро</h3>
                    <p className="text-gray-400">Анализ логов за секунды вместо часов ручной работы</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Shield className="w-6 h-6 text-atomic-accent flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">Точность анализа</h3>
                    <p className="text-gray-400">ML модель с 99% точностью обнаружения аномалий</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <TrendingUp className="w-6 h-6 text-atomic-accent flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">Real-time мониторинг</h3>
                    <p className="text-gray-400">Отслеживайте аномалии в реальном времени</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-6 h-6 text-atomic-accent flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">Production-ready</h3>
                    <p className="text-gray-400">Docker deployment за 1 команду</p>
                  </div>
                </div>
              </div>

              <Link to="/analyze" className="btn-primary inline-flex items-center mt-6">
                Начать анализ
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
            </div>

            {/* Demo screenshot placeholder */}
            <div className="card">
              <div className="aspect-video bg-gradient-to-br from-atomic-blue/20 to-atomic-accent/20 rounded-lg flex items-center justify-center">
                <Activity className="w-24 h-24 text-atomic-accent/50" />
              </div>
              <p className="text-center text-gray-400 mt-4">
                Скринкаст демонстрации будет здесь
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="card text-center space-y-6 bg-gradient-to-r from-atomic-blue/20 to-atomic-accent/20 border-atomic-blue/30">
            <h2 className="text-3xl md:text-4xl font-bold text-white">
              Готовы попробовать?
            </h2>
            <p className="text-xl text-gray-300">
              Загрузите логи и получите результат за секунды
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/analyze" className="btn-primary text-lg px-8 py-4">
                Анализировать логи
              </Link>
              <a href="https://t.me/AtomicHackLogBot" target="_blank" rel="noopener noreferrer" className="btn-secondary text-lg px-8 py-4">
                Telegram Bot
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

