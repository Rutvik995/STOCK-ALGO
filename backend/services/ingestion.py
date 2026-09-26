import yfinance as yf
from sqlalchemy.orm import Session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models import Stock, OHLCV
from datetime import datetime, timedelta

UNIVERSE_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "LARSEN.NS",
    "KOTAKBANK.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS"
]

def fetch_and_store_historical_data(db: Session, tickers=UNIVERSE_TICKERS, period="3y"):
    for ticker_symbol in tickers:
        print(f"Fetching data for {ticker_symbol}...")
        
        # Ensure stock exists in DB
        stock = db.query(Stock).filter(Stock.ticker == ticker_symbol).first()
        if not stock:
            stock = Stock(ticker=ticker_symbol, name=ticker_symbol, is_active=True)
            db.add(stock)
            db.commit()

        # Fetch data from yfinance
        df = yf.download(ticker_symbol, period=period, progress=False, auto_adjust=True)
        if df.empty:
            print(f"Warning: No data for {ticker_symbol}")
            continue

        if getattr(df.columns, 'nlevels', 1) > 1:
            df.columns = df.columns.droplevel(0)

        # Clear old data for this ticker (simple replacement strategy for MVP)
        db.query(OHLCV).filter(OHLCV.ticker == ticker_symbol).delete()
        
        ohlcv_records = []
        for index, row in df.iterrows():
            record = OHLCV(
                ticker=ticker_symbol,
                date=index.date(),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=float(row['Volume'])
            )
            ohlcv_records.append(record)
        
        db.bulk_save_objects(ohlcv_records)
        db.commit()
    print("Data ingestion complete.")
