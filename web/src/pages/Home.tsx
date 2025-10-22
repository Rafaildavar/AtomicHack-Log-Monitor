import { Link } from 'react-router-dom';
import { Activity, Shield, BarChart3, ArrowRight, Award, Cpu, GitBranch, Globe, Settings, MessageCircle, Package, Target, Zap, Lock } from 'lucide-react';
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

      {/* How It Works */}
      <section className="py-16 px-4 bg-atomic-dark">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Как это работает
            </h2>
            <p className="text-lg text-gray-400">
              4 простых шага до полного анализа ваших логов
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-4">
            {[
              { num: '1', title: 'Загрузите файл', desc: 'ZIP с логами или обычный TXT/LOG файл' },
              { num: '2', title: 'Выберите параметры', desc: 'Порог детектирования и словарь аномалий' },
              { num: '3', title: 'ML-анализ', desc: 'Система находит и классифицирует аномалии' },
              { num: '4', title: 'Получите отчет', desc: 'Excel с детальными результатами' }
            ].map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="card relative"
              >
                <div className="absolute -top-4 -right-4 w-10 h-10 bg-atomic-blue text-white rounded-full flex items-center justify-center font-bold text-lg">
                  {step.num}
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-gray-400">{step.desc}</p>
                {i < 3 && (
                  <ArrowRight className="absolute -right-8 top-1/2 transform -translate-y-1/2 text-atomic-blue hidden md:block" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-16 px-4 bg-gradient-to-b from-atomic-darker to-atomic-dark">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Сценарии использования
            </h2>
            <p className="text-lg text-gray-400">
              Решение для различных задач мониторинга
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                icon: Cpu,
                title: 'Мониторинг инфраструктуры',
                desc: 'Анализ логов серверов, базы данных, сетевых устройств для выявления критических ошибок'
              },
              {
                icon: Shield,
                title: 'Безопасность',
                desc: 'Обнаружение подозрительной активности и попыток несанкционированного доступа'
              },
              {
                icon: BarChart3,
                title: 'Аналитика производительности',
                desc: 'Выявление проблем с производительностью и узких мест в системе'
              },
              {
                icon: GitBranch,
                title: 'Отладка приложений',
                desc: 'Быстрый анализ логов приложений для поиска ошибок и исключений'
              }
            ].map((useCase, i) => {
              const Icon = useCase.icon;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="card group hover:border-atomic-blue/50 transition-all"
                >
                  <div className="w-12 h-12 rounded-lg bg-atomic-blue/20 flex items-center justify-center mb-4 group-hover:bg-atomic-blue/30 transition-all">
                    <Icon className="w-6 h-6 text-atomic-accent" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{useCase.title}</h3>
                  <p className="text-gray-400">{useCase.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Integration Examples */}
      <section className="py-16 px-4 bg-atomic-dark">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Методы интеграции
            </h2>
            <p className="text-lg text-gray-400">
              Выбирайте удобный способ интеграции в вашу систему
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                title: 'Веб-интерфейс',
                icon: Globe,
                desc: 'Удобный UI для анализа логов прямо в браузере',
                cta: 'Начать анализ',
                link: '/analyze',
                external: undefined
              },
              {
                title: 'REST API',
                icon: Settings,
                desc: 'Интеграция в ваши системы через HTTP API с JSON',
                cta: 'Документация API',
                link: '/docs',
                external: undefined
              },
              {
                title: 'Telegram Bot',
                icon: MessageCircle,
                desc: 'Быстрый анализ прямо из мессенджера',
                cta: 'Открыть бота',
                link: undefined,
                external: 'https://t.me/AtomicHackLogBot'
              }
            ].map((method, i) => {
              const MethodIcon = method.icon;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="card flex flex-col"
                >
                  <div className="w-12 h-12 rounded-lg bg-atomic-blue/20 flex items-center justify-center mb-4">
                    <MethodIcon className="w-6 h-6 text-atomic-accent" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{method.title}</h3>
                  <p className="text-gray-400 flex-1 mb-4">{method.desc}</p>
                  {method.external ? (
                    <a 
                      href={method.external} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-atomic-accent hover:text-atomic-blue transition-colors text-sm font-medium inline-flex items-center"
                    >
                      {method.cta} →
                    </a>
                  ) : method.link ? (
                    <Link 
                      to={method.link}
                      className="text-atomic-accent hover:text-atomic-blue transition-colors text-sm font-medium inline-flex items-center"
                    >
                      {method.cta} →
                    </Link>
                  ) : null}
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-4 bg-gradient-to-b from-atomic-darker to-atomic-dark">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { label: '500+', desc: 'Типов аномалий', icon: Package },
              { label: '90%', desc: 'Точность анализа', icon: Target },
              { label: '<5 сек', desc: 'Время обработки', icon: Zap },
              { label: '24/7', desc: 'Доступность', icon: Lock }
            ].map((stat, i) => {
              const StatIcon = stat.icon;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className="card text-center"
                >
                  <div className="flex justify-center mb-2">
                    <div className="w-12 h-12 rounded-lg bg-atomic-blue/20 flex items-center justify-center">
                      <StatIcon className="w-6 h-6 text-atomic-accent" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-atomic-accent mb-1">{stat.label}</div>
                  <div className="text-gray-400">{stat.desc}</div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-atomic-dark">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            className="card bg-gradient-to-r from-atomic-blue/20 to-atomic-accent/20 border-atomic-blue/50 text-center"
          >
            <Award className="w-16 h-16 text-atomic-accent mx-auto mb-4" />
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Готовы начать?
            </h2>
            <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
              Загрузите ваши логи и получите детальный анализ за считанные секунды
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/analyze" className="btn-primary text-lg px-8 py-4">
                Начать анализ
                <ArrowRight className="w-5 h-5 ml-2 inline" />
              </Link>
              <Link to="/about" className="btn-secondary text-lg px-8 py-4">
                Узнать больше
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
