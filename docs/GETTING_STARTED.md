# Getting Started - AI-Powered Insider Trading Detector

This guide will help you set up and run the insider trading detector system.

## Prerequisites

- Python 3.8+
- Supabase account
- Google Cloud Console account (for OAuth)
- Market data API access (Alpha Vantage or similar)

## Quick Setup

### 1. Clone and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup.py

# Test the system
python test_system.py
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
# Supabase (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Market Data API (required)
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

# Google OAuth (for frontend)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 3. Setup Supabase Database

1. Create a new Supabase project
2. Go to SQL Editor
3. Run the schema from `docs/supabase_schema.sql`
4. Enable Google OAuth in Authentication settings

### 4. Run the Pipeline

```bash
# Run complete pipeline
python main.py pipeline

# Or run individual steps
python main.py ingest     # Ingest market data
python main.py features   # Compute features
python main.py detect     # Detect anomalies

# Start API server
python main.py api
```

## System Architecture

```
Market Data APIs → Ingestion → Feature Engineering → ML Models → Anomaly Detection → Supabase → Dashboard
```

### Components

1. **Data Ingestion** (`backend/ingest/`)
   - Fetches market data from Yahoo Finance
   - Stores raw ticks in `market_ticks` table

2. **Feature Engineering** (`backend/models/feature_engineering.py`)
   - Computes rolling statistics
   - Calculates z-scores and momentum indicators
   - Stores features in `market_features` table

3. **Anomaly Detection** (`backend/models/anomaly_detector.py`)
   - Uses IsolationForest for unsupervised detection
   - Provides explainability via feature contributions
   - Stores anomalies in `anomalies` table

4. **API Server** (`backend/api/main.py`)
   - FastAPI server for ML inference
   - Real-time scoring endpoints
   - Background task processing

## Usage Examples

### Basic Pipeline Run

```bash
# This will:
# 1. Fetch market data for default tickers
# 2. Compute rolling features
# 3. Train/load ML model
# 4. Detect anomalies
python main.py pipeline
```

### API Usage

```bash
# Start the API server
python main.py api

# Test the API
curl http://localhost:8000/health
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# The API will be available at http://localhost:8000
```

## Configuration

### Tickers

Default tickers are configured in `backend/config.py`:

```python
default_tickers = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", 
    "ICICIBANK.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS"
]
```

### ML Parameters

- `ANOMALY_THRESHOLD`: Score threshold for flagging anomalies (default: 0.8)
- `CONTAMINATION_RATE`: Expected proportion of anomalies (default: 0.005)

### Feature Windows

Rolling windows for feature computation:
- 1 minute
- 5 minutes  
- 1 hour

## Monitoring

### Logs

Logs are stored in the `logs/` directory with daily rotation.

### Database

Check your Supabase dashboard for:
- `market_ticks`: Raw market data
- `market_features`: Computed features
- `anomalies`: Detected anomalies
- `alerts`: User notifications

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Connection Issues**
   - Check your Supabase URL and keys
   - Ensure RLS policies are set correctly

3. **No Market Data**
   - Verify your Alpha Vantage API key
   - Check if markets are open (Yahoo Finance has limited historical data)

4. **Model Training Fails**
   - Ensure you have sufficient data (at least 100 samples)
   - Check for NaN values in features

### Debug Mode

Run with debug logging:

```bash
export PYTHONPATH=.
python -c "
from loguru import logger
logger.add('debug.log', level='DEBUG')
# Your code here
"
```

## Next Steps

1. **Frontend Development**: Build the React dashboard
2. **Real-time Streaming**: Implement Kafka or WebSocket streaming
3. **Advanced ML**: Add Autoencoder and ensemble models
4. **Social Sentiment**: Integrate news and social media analysis
5. **Production Deployment**: Set up CI/CD and monitoring

## Support

- Check the logs in `logs/` directory
- Run `python test_system.py` to verify setup
- Review the database schema in `docs/supabase_schema.sql`

## Color Palette (for UI development)

- Primary: `#27d853` (success green)
- Danger: `#bf4040` (anomaly red)  
- Info: `#53acac` (teal)
- Purple: `#7f639c` (accent)
- Pink: `#9e618f` (accent)
- Muted: `#90886f` (text)