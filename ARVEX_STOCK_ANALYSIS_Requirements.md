# ARVEX STOCK ANALYSIS — System Requirements & Build Specification

## 1. Project Overview
ARVEX STOCK ANALYSIS is a personal-use web application for identifying and managing
**swing trade opportunities in the Indian stock market (NSE/BSE)**. It evolves the
existing "Stock Algo" prototype (Dash-based) into a more robust, better-risk-managed
system with a React.js frontend and a rule-based screening engine as the core
decision-making layer, with machine learning used only as a secondary confidence
signal — not the primary basis for a trade decision.

## 2. Objectives
- Identify short-to-medium-term (days-to-weeks) swing trade candidates across a wide,
  liquid universe of NSE stocks — not just a hardcoded list.
- Every flagged trade must come with a computed **entry, stop-loss, target, and
  position size** based on the user's risk settings — not just a "buy" signal.
- Every strategy used must be **backtestable and validated on historical Indian
  market data** before being trusted live.
- Replace the previous LSTM "price target" approach (regression, prone to
  autoregressive drift) with a **classification-based confidence signal**
  (probability of favorable move within N days), used only to rank/filter
  rule-based candidates.
- Fully migrate the UI to **React.js**, replacing the Dash frontend, served by a
  Python backend API.
- Reproducible results — the same inputs should produce the same output, no
  hidden randomness from on-the-fly model retraining per request.

## 3. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Frontend | React.js (Vite + TypeScript recommended) | Replaces Dash entirely |
| Charting | TradingView Lightweight Charts or Recharts | Candlestick + indicator overlays |
| Backend / API | Python, FastAPI | REST + WebSocket for live scan updates |
| Database | PostgreSQL | Matches your existing stack (Cortex, sales-data-agent) |
| Market Data | yfinance (EOD) + nsepython/jugaad-data (NSE bhavcopy) for a wider universe | Broker API (Kite/Upstox/Fyers) optional later for live/intraday |
| Backtesting | vectorbt or a custom pandas-based backtester | Must support walk-forward validation |
| ML (secondary signal) | scikit-learn (gradient boosting) or a lightweight classifier | Predicts P(price up X% in N days), not price level |
| Scheduling | APScheduler or Celery + Redis | For nightly universe scans, model retraining, EOD data refresh |
| Auth | JWT-based auth on the FastAPI backend | Replaces the current .env plaintext compare |

## 4. High-Level Architecture

```
[NSE/BSE Data Sources] ---> [Data Ingestion Service] ---> [PostgreSQL]
                                                              |
                                                              v
                                      [Rule-Based Screening Engine]  <-- configurable strategy rules
                                                              |
                                                              v
                                      [ML Confidence Layer] (classification, cached/scheduled, not per-request)
                                                              |
                                                              v
                                      [Risk & Position Sizing Module]
                                                              |
                                                              v
                                      [Backtesting Engine]  <-- validates strategies before they go live
                                                              |
                                                              v
                                      [FastAPI Backend / REST + WebSocket]
                                                              |
                                                              v
                                      [React.js Frontend Dashboard]
```

Screening and model inference run on a **scheduled job** (e.g., nightly after
market close), not synchronously inside a web request — this fixes the
synchronous-training bottleneck from the previous version.

## 5. Functional Modules

### 5.1 Authentication
- JWT-based login (single user is fine for personal use, but avoid plaintext
  password compare — hash with bcrypt at minimum).

### 5.2 Data Ingestion Layer
- Nightly EOD OHLCV fetch for the full liquidity-filtered universe (see 5.3).
- Store in PostgreSQL with a proper schema (ticker, date, OHLCV, adjusted close).
- Data quality checks: flag missing days, splits/bonus adjustments.

### 5.3 Swing Trade Screener (rule-based, deterministic)
- **Universe**: NIFTY 500 (or broader) filtered by a minimum average daily
  turnover threshold, instead of a hardcoded ~60-stock list — this ensures every
  candidate is liquid enough to actually trade.
- **Trend filter**: e.g., price above 50-day EMA (only consider longs in an
  uptrend context) — prevents "catching a falling knife" on oversold RSI in a
  downtrend.
- **Entry trigger** (configurable, pick one or combine):
  - EMA crossover (e.g., 20 EMA crosses above 50 EMA)
  - RSI(14) pullback into 40–50 range within an uptrend
  - Breakout above N-day high with volume ≥ 1.5–2x average
- **Confirmation filters**: relative strength vs. Nifty/sector, no major
  earnings/corporate action in the next N days.
- Strategy rules must be stored as **configuration**, not hardcoded, so they can
  be swapped and backtested independently.

### 5.4 Backtesting Engine
- Runs any configured strategy against 3–5 years of historical data for the
  full universe.
- Outputs: win rate, average R:R achieved, max drawdown, Sharpe/Sortino,
  equity curve, trade log.
- Must support walk-forward validation (train/test split over time), not just a
  single in-sample backtest, to reduce overfitting risk.
- No strategy is surfaced to the live screener until it has passed backtesting
  with acceptable metrics (thresholds configurable by the user).

### 5.5 Risk & Position Sizing Module
For every screened candidate, compute and display:
- **Stop-loss**: ATR-based (e.g., entry − 1.5×ATR) rather than a fixed
  percentage.
- **Target**: based on R:R multiple (configurable, e.g., minimum 1:2) and/or
  technical resistance/Fibonacci extension.
- **Position size**: `(capital × risk% ) / (entry − stop)`, where risk% and
  total capital are user-configurable settings (not hardcoded).
- **Portfolio-level checks**: max concurrent open positions, max sector
  exposure, running risk budget across all open trades.

### 5.6 ML Confidence Layer (secondary signal only)
- Predicts **probability of the trade reaching target before stop** (a
  classification problem), trained on engineered features (RSI, volume ratio,
  ATR, relative strength, etc.) — not raw price regression.
- Trained/retrained on a schedule (e.g., weekly), cached — never trained
  synchronously per request.
- Used to **rank or filter** rule-based candidates (e.g., "show only candidates
  the model scores above 60% confidence"), never as a standalone signal.
- Model outputs and the training data window are versioned/logged for
  auditability.

### 5.7 Portfolio Analyzer
- User enters current holdings (ticker, buy price, quantity).
- Shows current value, unrealized P&L, and — for holdings that also match an
  open swing rule — current stop/target status.
- Drop (or clearly relabel as speculative) the old per-holding LSTM "future
  value" price forecast, given the accuracy concerns already identified. If
  kept, must be visually flagged as low-confidence/speculative, not a
  projection.

### 5.8 Dashboard / Reporting
- Daily scan results with entry/stop/target/position size per candidate.
- Backtest report viewer per strategy.
- Trade journal (log of trades taken, outcome vs. plan) — useful for reviewing
  whether you're actually following the system's risk rules over time.

## 6. Non-Functional Requirements
- **Reproducibility**: identical inputs (date, strategy config) must produce
  identical outputs — no per-request random model retraining.
- **Performance**: nightly batch jobs for scanning/training; API responses to
  the frontend should be fast reads from precomputed results, not live
  computation.
- **Auditability**: every signal should be traceable to the exact rule/model
  version and data snapshot that produced it.
- **Security**: hashed credentials, environment-based secrets management, no
  hardcoded credentials in source.

## 7. React UI Requirements
- **Pages**:
  1. **Dashboard** — today's scan results as a sortable/filterable table
     (ticker, signal, entry, stop, target, R:R, ML confidence, position size).
  2. **Stock Detail** — candlestick chart with indicator overlays (EMA, RSI,
     volume), trade plan for that stock if flagged.
  3. **Strategy Config** — form to adjust screener rules, risk %, R:R
     minimum, universe filters.
  4. **Backtest Results** — equity curve, trade log, performance metrics per
     strategy version.
  5. **Portfolio** — current holdings, P&L, open-position risk summary.
  6. **Trade Journal** — log of trades taken vs. plan.
- **State management**: React Query (for server state/caching) + lightweight
  local state (Zustand or Context) — avoid Redux unless complexity grows.
- **Charting**: candlestick + overlay support is essential (TradingView
  Lightweight Charts is a strong fit and free).

## 8. API Endpoints (draft)
```
POST   /auth/login
GET    /scan/today                 -> today's screener results
GET    /stock/{ticker}/ohlcv       -> historical OHLCV + indicators
GET    /stock/{ticker}/plan        -> entry/stop/target/position size
POST   /strategy/config            -> update screener rule parameters
GET    /backtest/{strategy_id}     -> backtest report
POST   /backtest/run               -> trigger a new backtest run
GET    /portfolio                  -> current holdings + P&L
POST   /portfolio/holding          -> add/update a holding
GET    /journal                    -> trade journal entries
POST   /journal/entry              -> log a trade
```

## 9. Data Model (draft core tables)
```
stocks(ticker, name, sector, is_active)
ohlcv(ticker, date, open, high, low, close, volume)
strategy_config(id, name, rules_json, risk_pct, min_rr, is_active)
scan_results(id, strategy_id, ticker, date, signal, entry, stop, target,
             position_size, ml_confidence)
backtest_runs(id, strategy_id, run_date, win_rate, avg_rr, max_drawdown,
              sharpe, trade_log_json)
holdings(id, ticker, buy_price, quantity, buy_date)
journal_entries(id, ticker, entry_date, exit_date, entry_price, exit_price,
                 planned_stop, planned_target, outcome, notes)
```

## 10. Out of Scope (for this version) / Future Enhancements
- Live/intraday data and automated order placement via broker APIs
  (Kite/Upstox/Fyers) — can be added once the EOD-based system is validated.
- Natural-language querying / conversational interface over scan results —
  a natural fit to later expose as a goal on the Cortex platform, but not
  required for the core system to work.
- Multi-user support (currently single-user/personal use).
