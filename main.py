#!/usr/bin/env python3
"""
AI-Powered Insider Trading Detector
Main orchestration script for the complete pipeline.
"""

import argparse
import sys
from pathlib import Path
from loguru import logger

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.ingest.market_data import MarketDataIngester
from backend.models.feature_engineering import FeatureEngineer
from backend.models.anomaly_detector import AnomalyDetector
from backend.config import settings


def setup_logging():
    """Configure logging."""
    logger.add(
        "logs/insider_detector_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )


def run_ingestion():
    """Run market data ingestion."""
    logger.info("Starting market data ingestion")
    ingester = MarketDataIngester()
    results = ingester.ingest_all_tickers()
    
    total = sum(results.values())
    logger.info(f"Ingestion completed. Total records: {total}")
    
    for ticker, count in results.items():
        print(f"  {ticker}: {count} records")


def run_feature_engineering():
    """Run feature engineering."""
    logger.info("Starting feature engineering")
    engineer = FeatureEngineer()
    results = engineer.compute_features_all_tickers()
    
    total = sum(results.values())
    logger.info(f"Feature engineering completed. Total features: {total}")
    
    for ticker, count in results.items():
        print(f"  {ticker}: {count} feature records")


def run_anomaly_detection():
    """Run anomaly detection."""
    logger.info("Starting anomaly detection")
    detector = AnomalyDetector()
    
    # Load or train model
    if not detector.load_model():
        logger.info("Training new model...")
        # Training logic would go here
        logger.warning("Model training not implemented in this demo")
        return
    
    results = detector.process_all_tickers()
    
    total = sum(results.values())
    logger.info(f"Anomaly detection completed. Total anomalies: {total}")
    
    for ticker, count in results.items():
        print(f"  {ticker}: {count} anomalies detected")


def run_full_pipeline():
    """Run the complete pipeline."""
    logger.info("Starting full pipeline")
    
    print("🔄 Step 1: Ingesting market data...")
    run_ingestion()
    
    print("\n🔄 Step 2: Computing features...")
    run_feature_engineering()
    
    print("\n🔄 Step 3: Detecting anomalies...")
    run_anomaly_detection()
    
    print("\n✅ Pipeline completed successfully!")
    print(f"📊 Monitoring {len(settings.default_tickers)} tickers")
    print("🚨 Check your Supabase dashboard for detected anomalies")


def main():
    """Main entry point."""
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="AI-Powered Insider Trading Detector"
    )
    parser.add_argument(
        "command",
        choices=["ingest", "features", "detect", "pipeline", "api"],
        help="Command to run"
    )
    parser.add_argument(
        "--ticker",
        help="Specific ticker to process (optional)"
    )
    
    args = parser.parse_args()
    
    print("🚀 AI-Powered Insider Trading Detector")
    print("=" * 50)
    
    try:
        if args.command == "ingest":
            run_ingestion()
        elif args.command == "features":
            run_feature_engineering()
        elif args.command == "detect":
            run_anomaly_detection()
        elif args.command == "pipeline":
            run_full_pipeline()
        elif args.command == "api":
            print("🌐 Starting API server...")
            from backend.api.main import app
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8001)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n⏹️  Process stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
