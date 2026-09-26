import pandas as pd
from sqlalchemy.orm import Session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models import OHLCV, ScanResult, StrategyConfig
from datetime import datetime

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(period).mean()

def run_screener(db: Session, strategy_id: int):
    strategy = db.query(StrategyConfig).filter(StrategyConfig.id == strategy_id).first()
    if not strategy:
        print("Strategy not found")
        return
        
    rules = strategy.rules_json or {}
    risk_pct = strategy.risk_pct or 0.02 # default 2% risk
    min_rr = strategy.min_rr or 2.0
    
    capital = 100000 # Example fixed capital for simulation

    tickers = [t[0] for t in db.query(OHLCV.ticker).distinct().all()]
    
    results = []
    scan_date = datetime.now().date()
    
    # Delete old scan results for today for this strategy
    db.query(ScanResult).filter(ScanResult.strategy_id == strategy_id, ScanResult.date == scan_date).delete()

    for ticker in tickers:
        df = pd.read_sql(
            db.query(OHLCV).filter(OHLCV.ticker == ticker).order_by(OHLCV.date.asc()).statement, 
            db.bind
        )
        if df.empty or len(df) < 50:
            continue
            
        df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['RSI_14'] = calculate_rsi(df['close'], 14)
        df['ATR_14'] = calculate_atr(df, 14)
        
        last_row = df.iloc[-1]
        
        # Rule: Price > 50 EMA (Uptrend Context)
        is_uptrend = last_row['close'] > last_row['EMA_50']
        
        # Rule: RSI Pullback (e.g., between 40 and 50)
        is_rsi_pullback = 40 <= last_row['RSI_14'] <= 50
        
        if is_uptrend and is_rsi_pullback:
            entry_price = last_row['close']
            atr = last_row['ATR_14']
            
            # Risk & Position Sizing
            stop_loss = entry_price - (1.5 * atr)
            target = entry_price + (min_rr * (entry_price - stop_loss))
            
            risk_amount = capital * risk_pct
            risk_per_share = entry_price - stop_loss
            position_size = risk_amount / risk_per_share if risk_per_share > 0 else 0
            
            scan = ScanResult(
                strategy_id=strategy_id,
                ticker=ticker,
                date=scan_date,
                signal="BUY",
                entry=entry_price,
                stop=stop_loss,
                target=target,
                position_size=position_size,
                ml_confidence=None # Will be updated by ML layer
            )
            results.append(scan)
            
    db.bulk_save_objects(results)
    db.commit()
    print(f"Screener run complete. Found {len(results)} candidates.")
