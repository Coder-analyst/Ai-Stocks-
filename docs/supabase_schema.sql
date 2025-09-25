-- Supabase SQL Schema for Insider Trading Detector
-- Run these commands in your Supabase SQL editor

-- Enable Row Level Security
ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret';

-- Create profiles table (extends Supabase auth.users)
CREATE TABLE profiles (
    id uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
    display_name text,
    role text DEFAULT 'analyst',
    created_at timestamptz DEFAULT now()
);

-- Enable RLS on profiles
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own profile
CREATE POLICY "profiles_select_own" ON profiles
    FOR SELECT USING (auth.uid() = id);

-- Policy: Users can update their own profile
CREATE POLICY "profiles_update_own" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Raw market ticks (append-only)
CREATE TABLE market_ticks (
    id bigserial PRIMARY KEY,
    ts timestamptz NOT NULL,
    ticker text NOT NULL,
    price numeric(18,6) NOT NULL,
    volume bigint NOT NULL,
    exchange text,
    raw jsonb,
    created_at timestamptz DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_market_ticks_ticker_ts ON market_ticks (ticker, ts DESC);
CREATE INDEX idx_market_ticks_ts ON market_ticks (ts DESC);

-- Aggregated features snapshot
CREATE TABLE market_features (
    id bigserial PRIMARY KEY,
    ts timestamptz NOT NULL,
    ticker text NOT NULL,
    vol_rolling_5m numeric,
    vol_rolling_1h numeric,
    price_zscore numeric,
    derived jsonb,
    created_at timestamptz DEFAULT now()
);

-- Indexes for features
CREATE INDEX idx_market_features_ticker_ts ON market_features (ticker, ts DESC);
CREATE INDEX idx_market_features_ts ON market_features (ts DESC);

-- Anomaly results
CREATE TABLE anomalies (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker text NOT NULL,
    ts timestamptz NOT NULL,
    score numeric NOT NULL,
    model text NOT NULL,
    reason jsonb,
    raw_sample jsonb,
    flagged boolean DEFAULT true,
    created_at timestamptz DEFAULT now()
);

-- Indexes for anomalies
CREATE INDEX idx_anomalies_ticker ON anomalies (ticker);
CREATE INDEX idx_anomalies_created_at ON anomalies (created_at DESC);
CREATE INDEX idx_anomalies_score ON anomalies (score DESC);
CREATE INDEX idx_anomalies_flagged ON anomalies (flagged) WHERE flagged = true;

-- Enable RLS on anomalies
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;

-- Policy: Analysts can read all anomalies
CREATE POLICY "anomalies_select_analysts" ON anomalies
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role IN ('analyst', 'admin')
        )
    );

-- Alerts for users
CREATE TABLE alerts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    anomaly_id uuid REFERENCES anomalies(id),
    message text,
    severity text,
    sent_to uuid REFERENCES profiles(id),
    sent_at timestamptz,
    resolved boolean DEFAULT false,
    created_at timestamptz DEFAULT now()
);

-- Enable RLS on alerts
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own alerts
CREATE POLICY "alerts_select_own" ON alerts
    FOR SELECT USING (auth.uid() = sent_to);

-- Social mentions (for correlation analysis)
CREATE TABLE social_mentions (
    id bigserial PRIMARY KEY,
    ts timestamptz,
    platform text,
    ticker text,
    text text,
    sentiment real,
    raw jsonb,
    created_at timestamptz DEFAULT now()
);

-- Indexes for social mentions
CREATE INDEX idx_social_mentions_ticker_ts ON social_mentions (ticker, ts DESC);
CREATE INDEX idx_social_mentions_platform ON social_mentions (platform);

-- Model runs tracking
CREATE TABLE model_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name text NOT NULL,
    version text NOT NULL,
    training_date timestamptz NOT NULL,
    parameters jsonb,
    metrics jsonb,
    created_at timestamptz DEFAULT now()
);

-- Enable Realtime for live updates
ALTER PUBLICATION supabase_realtime ADD TABLE anomalies;
ALTER PUBLICATION supabase_realtime ADD TABLE alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE market_ticks;

-- Create a function to automatically create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name, role)
    VALUES (new.id, new.email, 'analyst');
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Sample data insertion function (for testing)
CREATE OR REPLACE FUNCTION insert_sample_anomaly()
RETURNS void AS $$
BEGIN
    INSERT INTO anomalies (ticker, ts, score, model, reason, raw_sample)
    VALUES (
        'RELIANCE.NS',
        now(),
        0.95,
        'isolation_forest_v1',
        '{"vol_zscore": 4.2, "price_momentum": 2.1, "social_sentiment": -0.8}',
        '{"vol_rolling_5m": 1500000, "vol_rolling_1h": 800000, "price_zscore": 4.2}'
    );
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;