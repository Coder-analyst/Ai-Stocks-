"""Market data ingestion from various sources."""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from loguru import logger
import time

from ..database import db
from ..storage_local import local_storage
from ..config import settings


class MarketDataIngester:
    """Ingests market data from Yahoo Finance and other sources."""
    
    def __init__(self):
        self.tickers = settings.default_tickers
    
    def fetch_historical_data(self, ticker: str, period: str = "1mo") -> pd.DataFrame:
        """Fetch historical data for a ticker."""
        try:
            stock = yf.Ticker(ticker)
            # Use daily data for more reliable results
            hist = stock.history(period=period, interval="1d")
            
            if hist.empty:
                logger.warning(f"No data found for {ticker}")
                return pd.DataFrame()
            
            # Reset index to get datetime as column
            hist = hist.reset_index()
            hist['ticker'] = ticker
            
            # Rename columns to match our expected format
            if 'Date' in hist.columns:
                hist = hist.rename(columns={'Date': 'Datetime'})
            
            return hist
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}: {e}")
            return pd.DataFrame()
    
    def ingest_ticker_data(self, ticker: str) -> int:
        """Ingest data for a single ticker and return number of records inserted."""
        logger.info(f"Ingesting data for {ticker}")
        
        df = self.fetch_historical_data(ticker)
        if df.empty:
            return 0
        
        # Prepare data for storage
        df['price'] = df['Close']
        df['volume'] = df['Volume']
        df['exchange'] = "NSE" if ticker.endswith('.NS') else "NYSE"
        
        # Use local storage (database fallback for when Supabase is configured)
        if settings.supabase_url and settings.supabase_url != "":
            # Try database first
            try:
                inserted_count = 0
                for _, row in df.iterrows():
                    success = db.insert_market_tick(
                        ticker=ticker,
                        price=float(row['Close']),
                        volume=int(row['Volume']),
                        timestamp=row['Datetime'],
                        exchange=row['exchange']
                    )
                    if success:
                        inserted_count += 1
                    time.sleep(0.01)
            except Exception as e:
                logger.warning(f"Database failed, using local storage: {e}")
                success = local_storage.save_market_ticks(ticker, df)
                inserted_count = len(df) if success else 0
        else:
            # Use local storage directly
            logger.info(f"Using local storage for {ticker}")
            success = local_storage.save_market_ticks(ticker, df)
            inserted_count = len(df) if success else 0
        
        logger.info(f"Inserted {inserted_count} records for {ticker}")
        return inserted_count
    
    def ingest_all_tickers(self) -> Dict[str, int]:
        """Ingest data for all configured tickers."""
        results = {}
        
        for ticker in self.tickers:
            try:
                count = self.ingest_ticker_data(ticker)
                results[ticker] = count
                
                # Delay between tickers to be respectful to the API
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to ingest {ticker}: {e}")
                results[ticker] = 0
        
        total_inserted = sum(results.values())
        logger.info(f"Total records inserted: {total_inserted}")
        
        return results
    
    def get_live_quote(self, ticker: str) -> Dict[str, Any]:
        """Get current live quote for a ticker."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'ticker': ticker,
                'price': info.get('currentPrice', 0),
                'volume': info.get('volume', 0),
                'timestamp': datetime.now(),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get live quote for {ticker}: {e}")
            return {}


def main():
    """Main function to run data ingestion."""
    logger.info("Starting market data ingestion")
    
    ingester = MarketDataIngester()
    results = ingester.ingest_all_tickers()
    
    logger.info("Ingestion completed")
    for ticker, count in results.items():
        print(f"{ticker}: {count} records")


if __name__ == "__main__":
    main()