from apscheduler.schedulers.background import BackgroundScheduler
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import SessionLocal
from services.ingestion import fetch_and_store_historical_data
from services.screener_engine import run_screener
from services.ml_engine import train_and_predict_confidence
from models import StrategyConfig

def nightly_job():
    print("Starting Nightly Batch Job...")
    db = SessionLocal()
    try:
        # 1. Fetch EOD Data
        fetch_and_store_historical_data(db)
        
        # 2. Run Screener for all active strategies
        strategies = db.query(StrategyConfig).filter(StrategyConfig.is_active == True).all()
        for strategy in strategies:
            run_screener(db, strategy.id)
            # 3. Apply ML Confidence
            train_and_predict_confidence(db, strategy.id)
            
    except Exception as e:
        print(f"Error in nightly job: {e}")
    finally:
        db.close()
    print("Nightly Batch Job Complete.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule to run every day at 18:00 (6:00 PM) after market close
    scheduler.add_job(nightly_job, 'cron', hour=18, minute=0)
    scheduler.start()
    return scheduler
