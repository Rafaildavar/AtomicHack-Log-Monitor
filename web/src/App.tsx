import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Home from './pages/Home';
import Analyze from './pages/Analyze';
import Results from './pages/Results';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  console.log('🚀 App loaded - Full version!');
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="flex flex-col min-h-screen bg-atomic-dark">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/analyze" element={<Analyze />} />
              <Route path="/results" element={<Results />} />
              <Route path="/dashboard" element={<div className="pt-24 px-4"><div className="container mx-auto"><h1 className="text-4xl font-bold text-white">Dashboard (Coming soon)</h1></div></div>} />
              <Route path="/history" element={<div className="pt-24 px-4"><div className="container mx-auto"><h1 className="text-4xl font-bold text-white">History (Coming soon)</h1></div></div>} />
              <Route path="/docs" element={<div className="pt-24 px-4"><div className="container mx-auto"><h1 className="text-4xl font-bold text-white">API Docs (Coming soon)</h1></div></div>} />
              <Route path="/about" element={<div className="pt-24 px-4"><div className="container mx-auto"><h1 className="text-4xl font-bold text-white">About (Coming soon)</h1></div></div>} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
