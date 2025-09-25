"""Configuration management for the insider trading detector."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    
    # Market data APIs
    alpha_vantage_api_key: str = ""
    iex_cloud_token: str = ""
    
    # Google OAuth (optional)
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # Monitoring (optional)
    sentry_dsn: str = ""
    
    # ML configuration
    model_version: str = "v1"
    anomaly_threshold: float = 0.8
    contamination_rate: float = 0.005
    
    # Default tickers to monitor (Indian stock market focus)
    default_tickers: List[str] = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
        "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
        "WIPRO.NS", "LT.NS", "MARUTI.NS", "ASIANPAINT.NS", "NESTLEIND.NS"
    ]
    
    # Feature engineering
    rolling_windows: List[str] = ["1min", "5min", "1h"]
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"  # Allow extra fields from .env
    }


settings = Settings()