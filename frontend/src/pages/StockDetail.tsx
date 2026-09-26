import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Activity, ShieldAlert, Target } from 'lucide-react';

export default function StockDetail() {
  const { ticker } = useParams();

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors mb-4">
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">{ticker}</h1>
            <p className="text-slate-400 mt-1">Technical Analysis & Trade Plan</p>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-800 shadow-xl overflow-hidden min-h-[400px] flex items-center justify-center p-6 relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5" />
            <div className="text-center z-10">
               <Activity className="h-12 w-12 text-slate-600 mx-auto mb-4 group-hover:text-indigo-400 transition-colors duration-500" />
               <p className="text-slate-400 font-medium">Chart visualization loading...</p>
               <p className="text-sm text-slate-500 mt-2 max-w-sm mx-auto">This area is reserved for the TradingView Lightweight Candlestick chart with EMA/RSI overlays.</p>
            </div>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-800 p-6 shadow-xl">
             <h3 className="font-bold text-white mb-4">System Trade Plan</h3>
             
             <div className="space-y-4">
                <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/50">
                   <div className="text-xs text-slate-400 uppercase font-semibold mb-1">Signal Type</div>
                   <div className="font-bold text-emerald-400 text-lg">BUY / LONG</div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/50">
                     <div className="text-xs text-slate-400 uppercase font-semibold mb-1">Entry Price</div>
                     <div className="font-bold text-white text-lg">₹--</div>
                  </div>
                  <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/50">
                     <div className="text-xs text-slate-400 uppercase font-semibold mb-1">R:R Ratio</div>
                     <div className="font-bold text-white text-lg">1:2.0</div>
                  </div>
                </div>
                
                <div className="p-4 rounded-xl border border-rose-900/30 bg-rose-950/20">
                   <div className="flex items-center gap-1.5 text-xs text-rose-400/80 uppercase font-semibold mb-1">
                     <ShieldAlert className="h-3.5 w-3.5" /> Stop Loss (ATR)
                   </div>
                   <div className="font-bold text-rose-400 text-lg">₹--</div>
                </div>
                
                <div className="p-4 rounded-xl border border-emerald-900/30 bg-emerald-950/20">
                   <div className="flex items-center gap-1.5 text-xs text-emerald-400/80 uppercase font-semibold mb-1">
                     <Target className="h-3.5 w-3.5" /> Target Price
                   </div>
                   <div className="font-bold text-emerald-400 text-lg">₹--</div>
                </div>
             </div>
             
             <button className="w-full mt-6 bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-lg font-bold transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-indigo-500/20">
               Execute Trade
             </button>
          </div>
          
          <div className="bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-800 p-6 shadow-xl">
             <h3 className="font-bold text-white mb-4">ML Confidence</h3>
             <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">Target probability</span>
                <span className="font-bold text-indigo-400">Evaluating...</span>
             </div>
             <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-slate-600 w-0" />
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
