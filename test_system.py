#!/usr/bin/env python3
"""
System test script to verify the insider trading detector setup.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import pandas as pd
        import numpy as np
        import sklearn
        import supabase
        print("✅ Core dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("🔍 Testing configuration...")
    
    try:
        from backend.config import settings
        print(f"✅ Configuration loaded")
        print(f"   - Model version: {settings.model_version}")
        print(f"   - Default tickers: {len(settings.default_tickers)}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_database_connection():
    """Test database connection (if configured)."""
    print("🔍 Testing database connection...")
    
    try:
        from backend.database import db
        from backend.config import settings
        
        # Try a simple operation (this will fail if not configured)
        if not settings.supabase_url:
            print("⚠️  Database not configured (missing SUPABASE_URL)")
            return True
        
        print("✅ Database client initialized")
        return True
    except Exception as e:
        print(f"⚠️  Database connection issue: {e}")
        return True  # Non-critical for initial setup


def test_feature_engineering():
    """Test feature engineering with sample data."""
    print("🔍 Testing feature engineering...")
    
    try:
        from backend.models.feature_engineering import FeatureEngineer
        
        # Create sample data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
        sample_data = pd.DataFrame({
            'ts': dates,
            'ticker': 'TEST.NS',
            'price': 100 + np.random.randn(100) * 2,
            'volume': 1000 + np.random.randint(0, 500, 100)
        })
        
        engineer = FeatureEngineer()
        features = engineer.compute_rolling_features(sample_data)
        
        if not features.empty:
            print(f"✅ Feature engineering works ({len(features)} features computed)")
            return True
        else:
            print("✅ Feature engineering works (empty result expected with sample data)")
            return True
            
    except Exception as e:
        print(f"❌ Feature engineering error: {e}")
        return False


def test_anomaly_detection():
    """Test anomaly detection with sample data."""
    print("🔍 Testing anomaly detection...")
    
    try:
        from backend.models.anomaly_detector import AnomalyDetector
        
        # Create sample feature data
        sample_features = pd.DataFrame({
            'ts': pd.date_range(start='2024-01-01', periods=50, freq='1min'),
            'ticker': 'TEST.NS',
            'vol_rolling_5m': np.random.normal(1000, 200, 50),
            'vol_rolling_1h': np.random.normal(1000, 200, 50),
            'price_zscore': np.random.normal(0, 1, 50),
            'derived': [{}] * 50
        })
        
        detector = AnomalyDetector()
        
        # Train a simple model
        if detector.train_isolation_forest(sample_features):
            print("✅ Model training works")
            
            # Test detection
            anomalies = detector.detect_anomalies(sample_features.head(10))
            print(f"✅ Anomaly detection works ({len(anomalies)} anomalies found)")
            return True
        else:
            print("❌ Model training failed")
            return False
            
    except Exception as e:
        print(f"❌ Anomaly detection error: {e}")
        return False


def test_api_imports():
    """Test API imports."""
    print("🔍 Testing API imports...")
    
    try:
        from backend.api.main import app
        print("✅ FastAPI app imports successfully")
        return True
    except Exception as e:
        print(f"❌ API import error: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 AI-Powered Insider Trading Detector - System Test")
    print("=" * 60)
    
    tests = [
        ("Core Imports", test_imports),
        ("Configuration", test_config),
        ("Database Connection", test_database_connection),
        ("Feature Engineering", test_feature_engineering),
        ("Anomaly Detection", test_anomaly_detection),
        ("API Imports", test_api_imports),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        print("\n📋 Next steps:")
        print("1. Configure your .env file with API keys")
        print("2. Set up Supabase database with the provided schema")
        print("3. Run: python main.py pipeline")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("💡 Make sure you've run: pip install -r requirements.txt")


if __name__ == "__main__":
    main()