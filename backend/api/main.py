"""FastAPI server for ML inference and data endpoints."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from datetime import datetime

from ..models.anomaly_detector import AnomalyDetector
from ..models.feature_engineering import FeatureEngineer
from ..ingest.market_data import MarketDataIngester
from ..database import db
from ..config import settings

app = FastAPI(
    title="Insider Trading Detector API",
    description="ML-powered anomaly detection for market data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
detector = AnomalyDetector()
engineer = FeatureEngineer()
ingester = MarketDataIngester()


class AnomalyRequest(BaseModel):
    """Request model for anomaly detection."""
    ticker: str
    features: Dict[str, float]


class AnomalyResponse(BaseModel):
    """Response model for anomaly detection."""
    ticker: str
    score: float
    is_anomaly: bool
    explanation: Dict[str, float]
    timestamp: datetime


@app.on_event("startup")
async def startup_event():
    """Load ML model on startup."""
    detector.load_model()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Insider Trading Detector API", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "model_loaded": detector.model is not None,
        "version": settings.model_version
    }


@app.post("/score", response_model=List[AnomalyResponse])
async def score_anomalies(requests: List[AnomalyRequest]):
    """Score anomalies for batch of features."""
    if detector.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    responses = []
    
    for req in requests:
        try:
            # Create a simple DataFrame for scoring
            import pandas as pd
            df = pd.DataFrame([{
                'ticker': req.ticker,
                'ts': datetime.now(),
                **req.features
            }])
            
            anomalies = detector.detect_anomalies(df)
            
            if anomalies:
                anomaly = anomalies[0]
                response = AnomalyResponse(
                    ticker=req.ticker,
                    score=anomaly['score'],
                    is_anomaly=anomaly['score'] > settings.anomaly_threshold,
                    explanation=anomaly['reason'],
                    timestamp=datetime.now()
                )
            else:
                response = AnomalyResponse(
                    ticker=req.ticker,
                    score=0.0,
                    is_anomaly=False,
                    explanation={},
                    timestamp=datetime.now()
                )
            
            responses.append(response)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing {req.ticker}: {str(e)}")
    
    return responses


@app.get("/anomalies/{ticker}")
async def get_anomalies(ticker: str, limit: int = 50):
    """Get recent anomalies for a ticker."""
    try:
        # This would typically query the database
        # For now, return a simple response
        return {
            "ticker": ticker,
            "anomalies": [],
            "count": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/{ticker}")
async def trigger_ingestion(ticker: str, background_tasks: BackgroundTasks):
    """Trigger data ingestion for a ticker."""
    background_tasks.add_task(ingester.ingest_ticker_data, ticker)
    return {"message": f"Ingestion started for {ticker}"}


@app.post("/features/{ticker}")
async def compute_features(ticker: str, background_tasks: BackgroundTasks):
    """Compute features for a ticker."""
    background_tasks.add_task(engineer.compute_features_for_ticker, ticker)
    return {"message": f"Feature computation started for {ticker}"}


@app.post("/detect/{ticker}")
async def detect_anomalies_endpoint(ticker: str, background_tasks: BackgroundTasks):
    """Detect anomalies for a ticker."""
    background_tasks.add_task(detector.process_ticker_anomalies, ticker)
    return {"message": f"Anomaly detection started for {ticker}"}


@app.get("/tickers")
async def get_tickers():
    """Get list of monitored tickers."""
    return {"tickers": settings.default_tickers}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)