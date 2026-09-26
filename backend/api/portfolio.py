from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import get_db
from models import Holding
from api.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class HoldingCreate(BaseModel):
    ticker: str
    buy_price: float
    quantity: float

@router.get("/")
def get_portfolio(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    holdings = db.query(Holding).all()
    return holdings

@router.post("/holding")
def add_holding(holding: HoldingCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_holding = Holding(ticker=holding.ticker, buy_price=holding.buy_price, quantity=holding.quantity)
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)
    return db_holding
