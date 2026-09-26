from fastapi import FastAPI
from database import engine
import models
from fastapi.middleware.cors import CORSMiddleware
from api import auth, screener, portfolio
from services.scheduler import start_scheduler
from contextlib import asynccontextmanager

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler = start_scheduler()
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(title="ARVEX Stock Analysis API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(screener.router, prefix="/scan", tags=["scan"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ARVEX Stock Analysis API"}
