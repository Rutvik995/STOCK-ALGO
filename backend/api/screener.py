from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import get_db
from models import ScanResult
from api.auth import get_current_user

router = APIRouter()

@router.get("/today")
def get_todays_scans(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    scan_date = datetime.now().date()
    results = db.query(ScanResult).filter(ScanResult.date == scan_date).all()
    return results

@router.post("/trigger")
def trigger_manual_scan(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    from services.scheduler import nightly_job
    nightly_job()
    return {"status": "Manual scan triggered"}
