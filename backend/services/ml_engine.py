import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestClassifier
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models import OHLCV, ScanResult
from datetime import datetime

def prepare_features(df):
    """
    Creates basic features for the classifier.
    """
    df['returns'] = df['close'].pct_change()
    df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
    
    # Target: Did it go up by 5% in the next 10 days?
    # (Simplified proxy for hitting target before stop)
    future_returns = df['close'].shift(-10) / df['close'] - 1
    df['target'] = (future_returns > 0.05).astype(int)
    
    df = df.dropna()
    
    features = ['RSI_14', 'ATR_14', 'volume_ratio', 'returns']
    return df, features

def train_and_predict_confidence(db: Session, strategy_id: int):
    """
    For MVP: Train a simple Random Forest on historical data 
    and assign a confidence score to today's scan results.
    """
    # 1. Gather all historical data for training (simplified across all tickers)
    print("Training ML Confidence layer...")
    tickers = [t[0] for t in db.query(OHLCV.ticker).distinct().all()]
    
    all_data = []
    for ticker in tickers[:5]: # limit for MVP speed
        df = pd.read_sql(
            db.query(OHLCV).filter(OHLCV.ticker == ticker).order_by(OHLCV.date.asc()).statement, 
            db.bind
        )
        if len(df) < 50:
            continue
            
        # Recreate features that screener used
        df['RSI_14'] = df['close'].diff().where(lambda x: x>0, 0).ewm(com=13).mean() / (df['close'].diff().where(lambda x: x<0, 0).abs().ewm(com=13).mean() + 1e-9)
        df['RSI_14'] = 100 - (100 / (1 + df['RSI_14']))
        df['ATR_14'] = df['high'] - df['low'] # simplified
        
        df, features = prepare_features(df)
        all_data.append(df)
        
    if not all_data:
        print("Not enough data to train ML.")
        return
        
    master_df = pd.concat(all_data)
    X = master_df[features]
    y = master_df['target']
    
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    
    # 2. Predict for today's scan results
    scan_date = datetime.now().date()
    scans = db.query(ScanResult).filter(ScanResult.strategy_id == strategy_id, ScanResult.date == scan_date).all()
    
    for scan in scans:
        df = pd.read_sql(
            db.query(OHLCV).filter(OHLCV.ticker == scan.ticker).order_by(OHLCV.date.asc()).statement, 
            db.bind
        )
        if len(df) < 50:
            continue
            
        df['RSI_14'] = df['close'].diff().where(lambda x: x>0, 0).ewm(com=13).mean() / (df['close'].diff().where(lambda x: x<0, 0).abs().ewm(com=13).mean() + 1e-9)
        df['RSI_14'] = 100 - (100 / (1 + df['RSI_14']))
        df['ATR_14'] = df['high'] - df['low'] # simplified
        
        df['returns'] = df['close'].pct_change()
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        
        current_features = df.iloc[-1][features].to_frame().T.fillna(0)
        
        try:
            proba = clf.predict_proba(current_features)[0]
            # Probability of class 1 (hitting target)
            confidence = float(proba[1]) * 100 
            scan.ml_confidence = confidence
        except IndexError:
            pass # fallback if only one class exists in small training set
        
    db.commit()
    print("ML Confidence applied to scan results.")
