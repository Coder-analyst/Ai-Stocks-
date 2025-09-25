# 🚀 Production Deployment Guide

This guide covers deploying the AI-Powered Insider Trading Detector to production.

## 📋 Prerequisites

- Python 3.8+
- Supabase account (for database)
- Domain name (optional)
- Cloud hosting (AWS/GCP/Azure/DigitalOcean)

## 🏗️ Architecture Overview

```
Internet → Load Balancer → Web Server → FastAPI → ML Models
                                    ↓
                              Supabase Database
                                    ↓
                              Real-time Updates
```

## 🔧 Step 1: Environment Setup

### 1.1 Clone and Setup
```bash
git clone <your-repo>
cd insider-trading-detector
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 1.2 Environment Variables
Create `.env` file:
```bash
# Database (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Market Data APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
IEX_CLOUD_TOKEN=your-iex-token

# Security
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,localhost

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO

# ML Configuration
MODEL_VERSION=v1
ANOMALY_THRESHOLD=0.8
CONTAMINATION_RATE=0.005
```

## 🗄️ Step 2: Database Setup

### 2.1 Supabase Configuration
1. Create new Supabase project
2. Run SQL schema from `docs/supabase_schema.sql`
3. Enable Row Level Security
4. Configure Google OAuth (optional)

### 2.2 Database Indexes
```sql
-- Performance indexes
CREATE INDEX CONCURRENTLY idx_market_ticks_ticker_ts ON market_ticks (ticker, ts DESC);
CREATE INDEX CONCURRENTLY idx_anomalies_score_desc ON anomalies (score DESC);
CREATE INDEX CONCURRENTLY idx_anomalies_created_at ON anomalies (created_at DESC);
```

## 🐳 Step 3: Docker Deployment

### 3.1 Build Images
```bash
# Build main application
docker build -t insider-detector:latest .

# Build with docker-compose
docker-compose build
```

### 3.2 Production Docker Compose
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - app
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

## 🌐 Step 4: Web Server Configuration

### 4.1 Nginx Configuration
```nginx
upstream app {
    server app:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /app/frontend/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4.2 SSL Configuration (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Step 5: Monitoring & Logging

### 5.1 Application Monitoring
```python
# Add to main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

### 5.2 System Monitoring
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

## 🔄 Step 6: CI/CD Pipeline

### 6.1 GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python test_system.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app && git pull && docker-compose up -d --build'
```

## 🔐 Step 7: Security Hardening

### 7.1 API Security
```python
# Add to FastAPI app
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "localhost"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 7.2 Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/anomalies")
@limiter.limit("10/minute")
async def get_anomalies(request: Request):
    # Your endpoint logic
    pass
```

## 📈 Step 8: Performance Optimization

### 8.1 Database Optimization
```sql
-- Partitioning for large tables
CREATE TABLE market_ticks_2025 PARTITION OF market_ticks
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Materialized views for analytics
CREATE MATERIALIZED VIEW daily_anomaly_summary AS
SELECT 
    DATE(created_at) as date,
    ticker,
    COUNT(*) as anomaly_count,
    AVG(score) as avg_score
FROM anomalies 
GROUP BY DATE(created_at), ticker;
```

### 8.2 Caching Strategy
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_result(expiry=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiry, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## 🚨 Step 9: Backup & Recovery

### 9.1 Database Backups
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > backups/backup_$DATE.sql
aws s3 cp backups/backup_$DATE.sql s3://your-backup-bucket/

# Cleanup old backups (keep 30 days)
find backups/ -name "*.sql" -mtime +30 -delete
```

### 9.2 Model Backups
```python
# Backup trained models
import joblib
from datetime import datetime

def backup_model(model, model_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/models/{model_name}_{timestamp}.joblib"
    joblib.dump(model, backup_path)
    
    # Upload to cloud storage
    # boto3.client('s3').upload_file(backup_path, 'bucket', backup_path)
```

## 📱 Step 10: Mobile API

### 10.1 Mobile-Optimized Endpoints
```python
@app.get("/api/mobile/summary")
async def mobile_summary():
    return {
        "total_anomalies": await get_anomaly_count(),
        "high_risk_tickers": await get_high_risk_tickers(limit=5),
        "system_status": "operational",
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/mobile/alerts")
async def mobile_alerts(limit: int = 10):
    return await get_recent_alerts(limit)
```

## 🎯 Step 11: Production Checklist

### Pre-Launch
- [ ] Environment variables configured
- [ ] Database schema deployed
- [ ] SSL certificates installed
- [ ] Monitoring setup (Sentry, logs)
- [ ] Backup strategy implemented
- [ ] Load testing completed
- [ ] Security audit passed

### Post-Launch
- [ ] Monitor error rates
- [ ] Check database performance
- [ ] Verify anomaly detection accuracy
- [ ] Monitor API response times
- [ ] Review security logs
- [ ] Test backup/recovery procedures

## 🔧 Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Monitor memory
   docker stats
   
   # Optimize ML models
   # Use model quantization or smaller models
   ```

2. **Database Connection Issues**
   ```python
   # Add connection pooling
   from sqlalchemy.pool import QueuePool
   
   engine = create_engine(
       DATABASE_URL,
       poolclass=QueuePool,
       pool_size=10,
       max_overflow=20
   )
   ```

3. **API Rate Limiting**
   ```python
   # Implement exponential backoff
   import asyncio
   
   async def retry_with_backoff(func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return await func()
           except Exception as e:
               if attempt == max_retries - 1:
                   raise
               await asyncio.sleep(2 ** attempt)
   ```

## 📞 Support

For production support:
- Check logs: `docker-compose logs -f app`
- Monitor health: `curl http://localhost:8000/health`
- Database status: Check Supabase dashboard
- Performance: Monitor Grafana dashboards

## 🎉 Congratulations!

Your AI-Powered Insider Trading Detector is now production-ready! 🚀

The system can handle:
- ✅ Real-time market data ingestion
- ✅ ML-powered anomaly detection
- ✅ Scalable web dashboard
- ✅ Production monitoring
- ✅ Automated deployments