import { Github, Mail, MessageCircle } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-atomic-darker border-t border-gray-800 mt-auto">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white">AtomicHack Log Monitor</h3>
            <p className="text-gray-400 text-sm">
              ИИ-анализатор журналов событий приложений с использованием ML для выявления аномалий.
            </p>
            <div className="flex space-x-3">
              <a
                href="https://github.com/Rafaildavar/AtomicHack-Log-Monitor"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://t.me/AtomicHackLogBot"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <MessageCircle className="w-5 h-5" />
              </a>
              <a
                href="mailto:team@blacklotus.dev"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Быстрые ссылки</h4>
            <ul className="space-y-2">
              <li>
                <a href="/analyze" className="text-gray-400 hover:text-white text-sm transition-colors">
                  Анализ логов
                </a>
              </li>
              <li>
                <a href="/dashboard" className="text-gray-400 hover:text-white text-sm transition-colors">
                  Real-time Dashboard
                </a>
              </li>
              <li>
                <a href="/history" className="text-gray-400 hover:text-white text-sm transition-colors">
                  История
                </a>
              </li>
              <li>
                <a href="/docs" className="text-gray-400 hover:text-white text-sm transition-colors">
                  API Документация
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Ресурсы</h4>
            <ul className="space-y-2">
              <li>
                <a href="https://github.com/Rafaildavar/AtomicHack-Log-Monitor" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white text-sm transition-colors">
                  GitHub Repository
                </a>
              </li>
              <li>
                <a href="/docs" className="text-gray-400 hover:text-white text-sm transition-colors">
                  API Reference
                </a>
              </li>
              <li>
                <a href="/docs" className="text-gray-400 hover:text-white text-sm transition-colors">
                  Integration Guide
                </a>
              </li>
              <li>
                <a href="https://t.me/AtomicHackLogBot" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white text-sm transition-colors">
                  Telegram Bot
                </a>
              </li>
            </ul>
          </div>

          {/* Team */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Команда</h4>
            <div className="space-y-2">
              <p className="text-white font-semibold">Black Lotus</p>
              <p className="text-sm text-gray-400">
                4-е место на AtomicHack Hackathon 2025
              </p>
              <p className="text-xs text-gray-500 mt-4">
                © 2025 Black Lotus. Все права защищены.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-sm text-gray-500">
              Разработано с использованием React, TypeScript, FastAPI
            </p>
            <div className="flex space-x-6 text-sm text-gray-500">
              <a href="/privacy" className="hover:text-white transition-colors">Политика конфиденциальности</a>
              <a href="/terms" className="hover:text-white transition-colors">Условия использования</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

