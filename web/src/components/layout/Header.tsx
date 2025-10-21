import { Link } from 'react-router-dom';
import { Activity, Github, Menu } from 'lucide-react';

export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-atomic-darker/80 backdrop-blur-lg border-b border-gray-800">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <Activity className="w-8 h-8 text-atomic-accent transition-transform group-hover:scale-110" />
              <div className="absolute inset-0 bg-atomic-accent/20 blur-xl group-hover:bg-atomic-accent/30 transition-all"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-white">AtomicHack</span>
              <span className="text-xs text-gray-400">Log Monitor</span>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className="text-gray-300 hover:text-white transition-colors font-medium"
            >
              Главная
            </Link>
            <Link 
              to="/analyze" 
              className="text-gray-300 hover:text-white transition-colors font-medium"
            >
              Анализ
            </Link>
            <Link 
              to="/dashboard" 
              className="text-gray-300 hover:text-white transition-colors font-medium"
            >
              Dashboard
            </Link>
            <Link 
              to="/history" 
              className="text-gray-300 hover:text-white transition-colors font-medium"
            >
              История
            </Link>
            <Link 
              to="/docs" 
              className="text-gray-300 hover:text-white transition-colors font-medium"
            >
              API Docs
            </Link>
            <Link 
              to="/about" 
              className="text-gray-300 hover:text-white transition-colors font-medium"
            >
              О проекте
            </Link>
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <a
              href="https://github.com/blacklotus-team/atomichack"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden md:flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition-all"
            >
              <Github className="w-5 h-5" />
              <span>GitHub</span>
            </a>
            
            <Link
              to="/analyze"
              className="btn-primary"
            >
              Попробовать
            </Link>

            {/* Mobile menu button */}
            <button className="md:hidden p-2 rounded-lg hover:bg-gray-800 transition-colors">
              <Menu className="w-6 h-6 text-gray-300" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

