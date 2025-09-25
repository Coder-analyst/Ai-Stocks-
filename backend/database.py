"""Database connection and operations using Supabase."""

from supabase import create_client, Client
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from loguru import logger

from .config import settings


class SupabaseDB:
    """Supabase database client for insider trading detector."""
    
    def __init__(self):
        if settings.supabase_url and settings.supabase_service_role_key:
            self.client: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
        else:
            self.client = None
    
    def insert_market_tick(self, ticker: str, price: float, volume: int, 
                          timestamp: datetime, exchange: str = "NSE") -> bool:
        """Insert a single market tick."""
        if not self.client:
            return False
            
        try:
            data = {
                "ts": timestamp.isoformat(),
                "ticker": ticker,
                "price": price,
                "volume": volume,
                "exchange": exchange,
                "raw": {}
            }
            
            result = self.client.table("market_ticks").insert(data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert market tick: {e}")
            return False
    
    def insert_market_features(self, features: Dict[str, Any]) -> bool:
        """Insert computed market features."""
        if not self.client:
            return False
            
        try:
            result = self.client.table("market_features").insert(features).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert market features: {e}")
            return False
    
    def insert_anomaly(self, ticker: str, timestamp: datetime, score: float,
                      model: str, reason: Dict[str, Any], 
                      raw_sample: Dict[str, Any]) -> bool:
        """Insert detected anomaly."""
        if not self.client:
            return False
            
        try:
            data = {
                "ticker": ticker,
                "ts": timestamp.isoformat(),
                "score": score,
                "model": model,
                "reason": reason,
                "raw_sample": raw_sample,
                "flagged": score > settings.anomaly_threshold
            }
            
            result = self.client.table("anomalies").insert(data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert anomaly: {e}")
            return False
    
    def get_recent_ticks(self, ticker: str, limit: int = 1000) -> pd.DataFrame:
        """Get recent market ticks for a ticker."""
        if not self.client:
            return pd.DataFrame()
            
        try:
            result = self.client.table("market_ticks")\
                .select("*")\
                .eq("ticker", ticker)\
                .order("ts", desc=True)\
                .limit(limit)\
                .execute()
            
            if result.data:
                df = pd.DataFrame(result.data)
                df['ts'] = pd.to_datetime(df['ts'])
                return df.sort_values('ts')
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to get recent ticks: {e}")
            return pd.DataFrame()
    
    def get_recent_features(self, ticker: str, limit: int = 100) -> pd.DataFrame:
        """Get recent computed features for a ticker."""
        if not self.client:
            return pd.DataFrame()
            
        try:
            result = self.client.table("market_features")\
                .select("*")\
                .eq("ticker", ticker)\
                .order("ts", desc=True)\
                .limit(limit)\
                .execute()
            
            if result.data:
                df = pd.DataFrame(result.data)
                df['ts'] = pd.to_datetime(df['ts'])
                return df.sort_values('ts')
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to get recent features: {e}")
            return pd.DataFrame()


# Global database instance
db = SupabaseDB()