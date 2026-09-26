import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import StockDetail from './pages/StockDetail';
import Portfolio from './pages/Portfolio';
import { Activity, LayoutDashboard, Briefcase } from 'lucide-react';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30">
        <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-2">
                <Activity className="h-8 w-8 text-indigo-500" />
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">
                  ARVEX
                </span>
              </div>
              <div className="flex space-x-4">
                <Link to="/" className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-slate-800 text-slate-300 hover:text-white transition-colors">
                  <LayoutDashboard className="h-4 w-4" /> Scanner
                </Link>
                <Link to="/portfolio" className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium hover:bg-slate-800 text-slate-300 hover:text-white transition-colors">
                  <Briefcase className="h-4 w-4" /> Portfolio
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/stock/:ticker" element={<StockDetail />} />
            <Route path="/portfolio" element={<Portfolio />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
