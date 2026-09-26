import { useState, useEffect } from 'react';
import axios from 'axios';
import { Briefcase, TrendingUp } from 'lucide-react';

export default function Portfolio() {
  const [holdings, setHoldings] = useState([]);
  
  useEffect(() => {
    axios.get('http://localhost:8000/portfolio')
      .then(res => setHoldings(res.data))
      .catch(console.error);
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Portfolio Analysis</h1>
        <p className="text-slate-400 mt-1">Manage your holdings and evaluate risk.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-800 p-6 shadow-xl">
          <div className="text-slate-400 text-sm font-medium">Total Invested</div>
          <div className="text-3xl font-bold text-white mt-2">₹0.00</div>
        </div>
        <div className="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-800 p-6 shadow-xl">
          <div className="text-slate-400 text-sm font-medium">Current Value</div>
          <div className="text-3xl font-bold text-emerald-400 mt-2">₹0.00</div>
        </div>
        <div className="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-800 p-6 shadow-xl">
          <div className="text-slate-400 text-sm font-medium">Unrealized P&L</div>
          <div className="text-3xl font-bold text-slate-500 mt-2">--</div>
        </div>
      </div>
      
      <div className="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-800 overflow-hidden shadow-2xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Briefcase className="h-5 w-5 text-indigo-400" /> Current Holdings
          </h2>
          <button className="text-sm bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
            + Add Position
          </button>
        </div>
        
        {holdings.length === 0 ? (
           <div className="text-center py-16 text-slate-500 bg-slate-950/30 rounded-xl border border-slate-800/50 border-dashed">
             <Briefcase className="h-8 w-8 mx-auto mb-3 text-slate-600" />
             <p className="font-medium">You have no holdings in your portfolio.</p>
             <p className="text-sm mt-1">Add positions to track your active trades against system rules.</p>
           </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/80 uppercase text-slate-400 text-xs font-semibold">
                <tr>
                  <th className="px-4 py-3">Ticker</th>
                  <th className="px-4 py-3">Buy Price</th>
                  <th className="px-4 py-3">Quantity</th>
                  <th className="px-4 py-3 text-right">Total Invested</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {holdings.map((h: any, i) => (
                  <tr key={i} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-4 font-bold text-white">{h.ticker}</td>
                    <td className="px-4 py-4">₹{h.buy_price.toFixed(2)}</td>
                    <td className="px-4 py-4">{h.quantity}</td>
                    <td className="px-4 py-4 text-right font-medium text-emerald-400">₹{(h.buy_price * h.quantity).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
