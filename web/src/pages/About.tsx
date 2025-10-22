import { motion } from 'framer-motion';
import { Award, Users, Zap, Code, Github, Linkedin } from 'lucide-react';

export default function About() {
  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            О проекте
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            AtomicHack Log Monitor - интеллектуальная система для анализа логов на базе машинного обучения
          </p>
        </motion.section>

        {/* Project Story */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-20"
        >
          <div className="card">
            <h2 className="text-3xl font-bold text-white mb-6">История проекта</h2>
            <div className="space-y-6 text-gray-300">
              <p>
                <span className="text-atomic-accent font-semibold">AtomicHack Log Monitor</span> родился на хакатоне 
                <span className="text-atomic-accent font-semibold"> AtomicHack 2025</span> как решение для критической задачи: 
                быстрого и точного анализа больших объёмов логов в системах мониторинга.
              </p>
              <p>
                Основная идея - использовать силу машинного обучения и семантического поиска для автоматического выявления 
                аномалий и критических проблем в логах, которые могут пропустить традиционные системы фильтрации.
              </p>
              <p>
                Проект разработан как модульная экосистема с тремя интерфейсами доступа:
              </p>
            </div>
          </div>
        </motion.section>

        {/* Architecture */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Архитектура решения</h2>
            <p className="text-gray-400">Три способа взаимодействия - одна мощная логика</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                title: '🤖 Telegram Bot',
                desc: 'Быстрый анализ прямо в мессенджере',
                features: ['Загрузка логов', 'Мгновенный анализ', 'Экспорт Excel']
              },
              {
                title: '⚙️ REST API',
                desc: 'Интеграция в любые системы',
                features: ['HTTP API', 'JSON responses', 'Swagger docs']
              },
              {
                title: '🌐 Веб-интерфейс',
                desc: 'Удобный UI для анализа',
                features: ['Drag & Drop', 'Визуализация', 'История']
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="card"
              >
                <h3 className="text-2xl font-bold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400 mb-4">{item.desc}</p>
                <ul className="space-y-2">
                  {item.features.map((feature, j) => (
                    <li key={j} className="text-sm text-gray-300 flex items-center">
                      <span className="w-1.5 h-1.5 rounded-full bg-atomic-accent mr-2"></span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Technologies */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Технологии</h2>
            <p className="text-gray-400">Современный стек для высокопроизводительного анализа</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                category: 'Machine Learning',
                tech: [
                  { name: 'Sentence Transformers', desc: 'Семантический поиск через embeddings' },
                  { name: 'PyTorch', desc: 'Глубокое обучение и вычисления' },
                  { name: 'Scikit-learn', desc: 'Обработка данных и ML утилиты' }
                ]
              },
              {
                category: 'Backend',
                tech: [
                  { name: 'FastAPI', desc: 'Высокопроизводительный REST API' },
                  { name: 'Uvicorn', desc: 'ASGI сервер для Python' },
                  { name: 'Pandas', desc: 'Анализ и обработка табличных данных' }
                ]
              },
              {
                category: 'Frontend',
                tech: [
                  { name: 'React 18', desc: 'Современный UI фреймворк' },
                  { name: 'TypeScript', desc: 'Типизированный JavaScript' },
                  { name: 'TailwindCSS', desc: 'Утилитарный CSS фреймворк' }
                ]
              },
              {
                category: 'Интеграция',
                tech: [
                  { name: 'Aiogram 3', desc: 'Telegram Bot API' },
                  { name: 'Docker', desc: 'Контейнеризация сервисов' },
                  { name: 'GitHub Actions', desc: 'CI/CD pipeline' }
                ]
              }
            ].map((section, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="card"
              >
                <h3 className="text-xl font-bold text-atomic-accent mb-4">{section.category}</h3>
                <div className="space-y-3">
                  {section.tech.map((item, j) => (
                    <div key={j} className="border-b border-gray-700 pb-3 last:border-0">
                      <p className="font-semibold text-white">{item.name}</p>
                      <p className="text-sm text-gray-400">{item.desc}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Achievements */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Достижения</h2>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {[
              { icon: '🏆', title: '4-е место', desc: 'AtomicHack Hackathon 2025' },
              { icon: '⚡', title: '<5 сек', desc: 'Время анализа' },
              { icon: '🎯', title: '90%', desc: 'Точность' },
              { icon: '📦', title: '500+', desc: 'Типов аномалий' }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                className="card text-center"
              >
                <div className="text-4xl mb-3">{item.icon}</div>
                <h3 className="text-xl font-bold text-white mb-1">{item.title}</h3>
                <p className="text-sm text-gray-400">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Key Features */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Ключевые возможности</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                icon: Zap,
                title: 'Реальное время',
                desc: 'Анализ логов в режиме реального времени с моментальной обработкой'
              },
              {
                icon: Award,
                title: 'Высокая точность',
                desc: 'ML-модель обучена на тысячах примеров для максимальной точности'
              },
              {
                icon: Code,
                title: 'API интеграция',
                desc: 'REST API для интеграции в существующие системы мониторинга'
              },
              {
                icon: Users,
                title: 'Масштабируемость',
                desc: 'Может обрабатывать огромные объемы логов параллельно'
              }
            ].map((item, i) => {
              const Icon = item.icon;
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
                  <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                  <p className="text-gray-400">{item.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </motion.section>

        {/* Team */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Команда Black Lotus 🌸</h2>
            <p className="text-gray-400">Разработчики, ML-специалисты и дизайнеры</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                name: 'ML & Backend',
                role: 'Разработка ядра системы',
                skills: ['Python', 'FastAPI', 'ML', 'Docker']
              },
              {
                name: 'Frontend & UX',
                role: 'Веб и мобильный интерфейс',
                skills: ['React', 'TypeScript', 'Design', 'UX']
              },
              {
                name: 'Bot & Integration',
                role: 'Telegram бот и интеграции',
                skills: ['Aiogram', 'API', 'Integration', 'DevOps']
              }
            ].map((member, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="card text-center"
              >
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-atomic-blue to-atomic-accent mx-auto mb-4 flex items-center justify-center">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-1">{member.name}</h3>
                <p className="text-atomic-accent text-sm mb-3">{member.role}</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {member.skills.map((skill, j) => (
                    <span key={j} className="text-xs px-2 py-1 rounded-full bg-atomic-blue/20 text-gray-300">
                      {skill}
                    </span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Open Source */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mb-20"
        >
          <div className="card bg-gradient-to-r from-atomic-blue/20 to-atomic-accent/20 border-atomic-blue/50 text-center">
            <Github className="w-16 h-16 text-atomic-accent mx-auto mb-4" />
            <h2 className="text-3xl font-bold text-white mb-4">Open Source</h2>
            <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
              Проект разработан как открытый источник для того, чтобы сообщество могло использовать и улучшать решение
            </p>
            <a
              href="https://github.com/Rafaildavar/AtomicHack-Log-Monitor"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 btn-primary"
            >
              <Github className="w-5 h-5" />
              <span>Посмотреть на GitHub</span>
            </a>
          </div>
        </motion.section>

        {/* Contact */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h2 className="text-3xl font-bold text-white mb-6">Контакты</h2>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
            <a
              href="https://t.me/AtomicHackLogBot"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary inline-flex items-center space-x-2"
            >
              <span>📱 Telegram Bot</span>
            </a>
            <a
              href="https://github.com/Rafaildavar/AtomicHack-Log-Monitor"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary inline-flex items-center space-x-2"
            >
              <Github className="w-5 h-5" />
              <span>GitHub</span>
            </a>
          </div>
        </motion.section>
      </div>
    </div>
  );
}
