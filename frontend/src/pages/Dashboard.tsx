import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Target, ShieldAlert, ArrowRight, Activity } from 'lucide-react';

export default function Dashboard() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, we'd use React Query and handle JWT auth
    axios.get('http://localhost:8000/scan/today')
      .then(res => {
        setScans(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Daily Swing Scan</h1>
          <p className="text-slate-400 mt-1">Rule-based candidates for today</p>
        </div>
        <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg font-medium shadow-lg shadow-indigo-500/20 transition-all hover:scale-105 active:scale-95">
          Run Scanner
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-32">
          <Activity className="h-10 w-10 animate-spin text-indigo-500" />
        </div>
      ) : (
        <div className="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-800 overflow-hidden shadow-2xl shadow-black/50">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-slate-950/80 uppercase text-slate-400 text-xs font-semibold tracking-wider">
                <tr>
                  <th className="px-6 py-5">Ticker</th>
                  <th className="px-6 py-5">Signal</th>
                  <th className="px-6 py-5">Entry</th>
                  <th className="px-6 py-5">Stop Loss</th>
                  <th className="px-6 py-5">Target</th>
                  <th className="px-6 py-5">ML Conf</th>
                  <th className="px-6 py-5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {scans.length > 0 ? scans.map((scan: any, i) => (
                  <tr key={i} className="hover:bg-slate-800/50 transition-colors group">
                    <td className="px-6 py-4 font-bold text-white">{scan.ticker}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 py-1 px-2.5 rounded-md text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {scan.signal}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-200">₹{scan.entry.toFixed(2)}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 text-rose-400 bg-rose-500/10 px-2 py-1 rounded-md w-fit">
                        <ShieldAlert className="h-3.5 w-3.5" /> ₹{scan.stop.toFixed(2)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-md w-fit">
                        <Target className="h-3.5 w-3.5" /> ₹{scan.target.toFixed(2)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-20 h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all duration-1000 ease-out ${scan.ml_confidence > 50 ? 'bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.5)]' : 'bg-slate-500'}`} 
                            style={{ width: `${scan.ml_confidence || 0}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-slate-300">
                          {scan.ml_confidence ? `${scan.ml_confidence.toFixed(1)}%` : 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link to={`/stock/${scan.ticker}`} className="inline-flex items-center justify-end gap-1.5 text-indigo-400 hover:text-indigo-300 font-medium transition-colors group-hover:translate-x-1 duration-200">
                        Analyze <ArrowRight className="h-4 w-4" />
                      </Link>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={7} className="px-6 py-16 text-center text-slate-500">
                      <div className="flex flex-col items-center gap-2">
                        <Activity className="h-8 w-8 text-slate-600 mb-2" />
                        <p className="text-lg font-medium text-slate-400">No scan results for today</p>
                        <p className="text-sm">The market might not have hit your configured technical rules.</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
