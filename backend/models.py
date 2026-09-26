from sqlalchemy import Column, Integer, String, Float, Boolean, Date, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Stock(Base):
    __tablename__ = "stocks"
    ticker = Column(String, primary_key=True, index=True)
    name = Column(String)
    sector = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class OHLCV(Base):
    __tablename__ = "ohlcv"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, ForeignKey("stocks.ticker"), index=True)
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

class StrategyConfig(Base):
    __tablename__ = "strategy_config"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    rules_json = Column(JSON)
    risk_pct = Column(Float)
    min_rr = Column(Float)
    is_active = Column(Boolean, default=True)

class ScanResult(Base):
    __tablename__ = "scan_results"
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategy_config.id"))
    ticker = Column(String, ForeignKey("stocks.ticker"))
    date = Column(Date)
    signal = Column(String) # BUY / SELL
    entry = Column(Float)
    stop = Column(Float)
    target = Column(Float)
    position_size = Column(Float)
    ml_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())

class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategy_config.id"))
    run_date = Column(DateTime, default=func.now())
    win_rate = Column(Float)
    avg_rr = Column(Float)
    max_drawdown = Column(Float)
    sharpe = Column(Float)
    trade_log_json = Column(JSON)

class Holding(Base):
    __tablename__ = "holdings"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, ForeignKey("stocks.ticker"))
    buy_price = Column(Float)
    quantity = Column(Float)
    buy_date = Column(Date, nullable=True)

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, ForeignKey("stocks.ticker"))
    entry_date = Column(Date)
    exit_date = Column(Date, nullable=True)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    planned_stop = Column(Float)
    planned_target = Column(Float)
    outcome = Column(String, nullable=True) # WIN, LOSS, BREAKEVEN, OPEN
    notes = Column(String, nullable=True)
