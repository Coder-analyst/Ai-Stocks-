"""Local file storage as fallback when Supabase is not configured."""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger


class LocalStorage:
    """Local file storage for market data when database is not available."""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "ticks").mkdir(exist_ok=True)
        (self.data_dir / "features").mkdir(exist_ok=True)
        (self.data_dir / "anomalies").mkdir(exist_ok=True)
    
    def save_market_ticks(self, ticker: str, data: pd.DataFrame) -> bool:
        """Save market tick data to CSV."""
        try:
            file_path = self.data_dir / "ticks" / f"{ticker}.csv"
            
            # Append to existing file or create new
            if file_path.exists():
                existing_data = pd.read_csv(file_path)
                combined_data = pd.concat([existing_data, data], ignore_index=True)
                combined_data.drop_duplicates(subset=['Datetime'], keep='last', inplace=True)
                combined_data.to_csv(file_path, index=False)
            else:
                data.to_csv(file_path, index=False)
            
            logger.info(f"Saved {len(data)} ticks for {ticker} to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save ticks for {ticker}: {e}")
            return False
    
    def load_market_ticks(self, ticker: str, limit: int = 1000) -> pd.DataFrame:
        """Load market tick data from CSV."""
        try:
            file_path = self.data_dir / "ticks" / f"{ticker}.csv"
            
            if not file_path.exists():
                return pd.DataFrame()
            
            data = pd.read_csv(file_path)
            data['Datetime'] = pd.to_datetime(data['Datetime'])
            
            # Return most recent records
            data = data.sort_values('Datetime').tail(limit)
            return data
            
        except Exception as e:
            logger.error(f"Failed to load ticks for {ticker}: {e}")
            return pd.DataFrame()
    
    def save_features(self, ticker: str, features: pd.DataFrame) -> bool:
        """Save computed features to CSV."""
        try:
            file_path = self.data_dir / "features" / f"{ticker}_features.csv"
            
            if file_path.exists():
                existing_data = pd.read_csv(file_path)
                combined_data = pd.concat([existing_data, features], ignore_index=True)
                combined_data.drop_duplicates(subset=['ts'], keep='last', inplace=True)
                combined_data.to_csv(file_path, index=False)
            else:
                features.to_csv(file_path, index=False)
            
            logger.info(f"Saved {len(features)} features for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save features for {ticker}: {e}")
            return False
    
    def load_features(self, ticker: str, limit: int = 100) -> pd.DataFrame:
        """Load computed features from CSV."""
        try:
            file_path = self.data_dir / "features" / f"{ticker}_features.csv"
            
            if not file_path.exists():
                return pd.DataFrame()
            
            data = pd.read_csv(file_path)
            data['ts'] = pd.to_datetime(data['ts'])
            
            return data.sort_values('ts').tail(limit)
            
        except Exception as e:
            logger.error(f"Failed to load features for {ticker}: {e}")
            return pd.DataFrame()
    
    def save_anomalies(self, anomalies: List[Dict[str, Any]]) -> bool:
        """Save detected anomalies to JSON."""
        try:
            file_path = self.data_dir / "anomalies" / "anomalies.json"
            
            # Load existing anomalies
            existing_anomalies = []
            if file_path.exists():
                with open(file_path, 'r') as f:
                    existing_anomalies = json.load(f)
            
            # Add new anomalies
            for anomaly in anomalies:
                # Convert datetime to string for JSON serialization
                if isinstance(anomaly.get('timestamp'), datetime):
                    anomaly['timestamp'] = anomaly['timestamp'].isoformat()
                existing_anomalies.append(anomaly)
            
            # Save back to file
            with open(file_path, 'w') as f:
                json.dump(existing_anomalies, f, indent=2, default=str)
            
            logger.info(f"Saved {len(anomalies)} anomalies")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save anomalies: {e}")
            return False
    
    def load_anomalies(self, ticker: str = None) -> List[Dict[str, Any]]:
        """Load anomalies from JSON."""
        try:
            file_path = self.data_dir / "anomalies" / "anomalies.json"
            
            if not file_path.exists():
                return []
            
            with open(file_path, 'r') as f:
                anomalies = json.load(f)
            
            # Filter by ticker if specified
            if ticker:
                anomalies = [a for a in anomalies if a.get('ticker') == ticker]
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to load anomalies: {e}")
            return []


# Global storage instance
local_storage = LocalStorage()