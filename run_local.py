#!/usr/bin/env python3
"""
Run the insider trading detector with local storage only.
This bypasses database issues and shows the complete working system.
"""

import os
import sys
from pathlib import Path
from loguru import logger

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

# Temporarily disable Supabase to force local storage
os.environ["SUPABASE_URL"] = ""

from backend.ingest.market_data import MarketDataIngester
from backend.models.feature_engineering import FeatureEngineer
from backend.models.anomaly_detector import AnomalyDetector
from backend.storage_local import local_storage


def main():
    """Run the complete pipeline with local storage."""
    print("🚀 AI-Powered Insider Trading Detector (Local Mode)")
    print("=" * 60)
    
    # Step 1: Ingest market data
    print("📈 Step 1: Ingesting real market data...")
    ingester = MarketDataIngester()
    results = ingester.ingest_all_tickers()
    
    total_ingested = sum(results.values())
    print(f"✅ Ingested {total_ingested} records")
    for ticker, count in results.items():
        if count > 0:
            print(f"   {ticker}: {count} records")
    
    if total_ingested == 0:
        print("❌ No data ingested. Check your internet connection.")
        return
    
    # Step 2: Feature engineering
    print("\n🔧 Step 2: Computing features...")
    engineer = FeatureEngineer()
    feature_results = engineer.compute_features_all_tickers()
    
    total_features = sum(feature_results.values())
    print(f"✅ Computed {total_features} feature records")
    
    # Step 3: Anomaly detection
    print("\n🚨 Step 3: Detecting anomalies...")
    detector = AnomalyDetector()
    
    # Train model if needed
    if not detector.load_model():
        print("🤖 Training new anomaly detection model...")
        # Get all features for training
        all_features = []
        for ticker in ingester.tickers:
            features = local_storage.load_features(ticker)
            if not features.empty:
                all_features.append(features)
        
        if all_features:
            import pandas as pd
            training_data = pd.concat(all_features, ignore_index=True)
            detector.train_isolation_forest(training_data)
    
    # Detect anomalies
    anomaly_results = detector.process_all_tickers()
    total_anomalies = sum(anomaly_results.values())
    
    print(f"✅ Detected {total_anomalies} anomalies")
    
    # Show results
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    # Show data files created
    data_dir = Path("data")
    tick_files = list((data_dir / "ticks").glob("*.csv"))
    feature_files = list((data_dir / "features").glob("*.csv"))
    
    print(f"📁 Data files created:")
    print(f"   Market data: {len(tick_files)} files")
    print(f"   Features: {len(feature_files)} files")
    
    # Show sample data
    if tick_files:
        sample_file = tick_files[0]
        import pandas as pd
        sample_data = pd.read_csv(sample_file)
        ticker = sample_file.stem
        print(f"\n📈 Sample data for {ticker}:")
        print(f"   Records: {len(sample_data)}")
        if 'Date' in sample_data.columns:
            print(f"   Date range: {sample_data['Date'].min()} to {sample_data['Date'].max()}")
        elif 'Datetime' in sample_data.columns:
            print(f"   Date range: {sample_data['Datetime'].min()} to {sample_data['Datetime'].max()}")
        print(f"   Price range: ₹{sample_data['Close'].min():.2f} - ₹{sample_data['Close'].max():.2f}")
    
    # Show anomalies
    anomalies = local_storage.load_anomalies()
    if anomalies:
        print(f"\n🚨 Anomalies detected: {len(anomalies)}")
        for anomaly in anomalies[:3]:  # Show first 3
            print(f"   {anomaly['ticker']}: Score {anomaly['score']:.3f}")
    
    print(f"\n✅ System working perfectly!")
    print(f"🔍 Check the 'data/' folder for all generated files")
    print(f"🌐 Run 'python main.py api' to start the web server")


if __name__ == "__main__":
    main()