"""
Configuration settings for Indian Stock Portfolio Optimization
"""
from datetime import datetime, timedelta
import pandas as pd

PORTFOLIO_TICKERS = [
    "RELIANCE.NS",      # Energy & Petrochemicals
    "TCS.NS",           # IT Services
    "HDFCBANK.NS",      # Private Bank
    "INFY.NS",          # IT Services
    "ICICIBANK.NS",     # Private Bank
    "HINDUNILVR.NS",    # FMCG
    "ITC.NS",           # FMCG & Tobacco
    "SBIN.NS",          # Public Sector Bank
    "BHARTIARTL.NS",    # Telecom
    "LT.NS",            # Infrastructure
]


# Historical data range
START_DATE = "2023-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

# For forecasting
FORECAST_PERIODS = 1  # Days ahead to forecast
RISK_AVERSION = 3.0

# Minimum allocation per asset (to avoid too small positions)
# 0.05 = 5% minimum per stock
MINIMUM_ALLOCATION = 0.05

# Maximum allocation per asset (to ensure diversification)
# 0.30 = 30% maximum per stock
MAXIMUM_ALLOCATION = 0.30

# Allow short positions? (For Indian retail, typically False)
ALLOW_SHORT = False


# Prophet model settings
PROPHET_PARAMS = {
    'daily_seasonality': True,
    'weekly_seasonality': True,
    'yearly_seasonality': True,
    'changepoint_prior_scale': 0.05,  # Flexibility of trend changes
    'seasonality_prior_scale': 10,     # Strength of seasonality
}

# NSE Trading Holidays
INDIAN_MARKET_HOLIDAYS = pd.DataFrame({
    'holiday': 'indian_market_holiday',
    'ds': pd.to_datetime([
       
        '2025-01-26',  # Republic Day
        '2025-03-08',  # Maha Shivaratri
        '2025-03-25',  # Holi
        '2025-03-29',  # Good Friday
        '2025-04-11',  # Id-Ul-Fitr
        '2025-04-17',  # Ram Navami
        '2025-04-21',  # Mahavir Jayanti
        '2025-05-01',  # Maharashtra Day
        '2025-05-23',  # Buddha Purnima
        '2025-06-17',  # Bakri Id
        '2025-07-17',  # Muharram
        '2025-08-15',  # Independence Day
        '2025-08-26',  # Janmashtami
        '2025-10-02',  # Gandhi Jayanti
        '2025-10-12',  # Dussehra
        '2025-11-01',  # Diwali (Laxmi Puja)
        '2025-11-02',  # Diwali Balipratipada
        '2025-11-15',  # Gurunanak Jayanti
        '2025-12-25',  # Christmas
        
        
        '2026-01-26',  # Republic Day
        '2026-03-14',  # Holi
        '2026-03-31',  # Id-Ul-Fitr
        '2026-04-10',  # Mahavir Jayanti
        '2026-04-14',  # Dr. Ambedkar Jayanti
        '2026-04-18',  # Good Friday
        '2026-05-01',  # Maharashtra Day
        '2026-08-15',  # Independence Day
        '2026-10-02',  # Gandhi Jayanti
        '2026-11-05',  # Gurunanak Jayanti
        '2026-12-25',  # Christmas
    ]),
    'lower_window': 0,
    'upper_window': 0,
})

# Market timezone
MARKET_TIMEZONE = "Asia/Kolkata"

# Currency
CURRENCY_SYMBOL = "₹"
CURRENCY_CODE = "INR"

# Market hours (IST)
MARKET_OPEN = "09:15"   # 9:15 AM
MARKET_CLOSE = "15:30"  # 3:30 PM
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Table name for storing results
RESULTS_TABLE = "portfolio_predictions"

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Supabase table name
SUPABASE_TABLE_NAME = RESULTS_TABLE  
HOLIDAY_NAME_MAP = {} 

def validate_settings():
    """Validate configuration settings"""
    errors = []
    
    if not PORTFOLIO_TICKERS:
        errors.append("PORTFOLIO_TICKERS cannot be empty")
    
    if RISK_AVERSION <= 0:
        errors.append("RISK_AVERSION must be positive")
    
    if not (0 <= MINIMUM_ALLOCATION <= 1):
        errors.append("MINIMUM_ALLOCATION must be between 0 and 1")
    
    if not (0 <= MAXIMUM_ALLOCATION <= 1):
        errors.append("MAXIMUM_ALLOCATION must be between 0 and 1")
    
    if MINIMUM_ALLOCATION > MAXIMUM_ALLOCATION:
        errors.append("MINIMUM_ALLOCATION cannot exceed MAXIMUM_ALLOCATION")
    
    if len(PORTFOLIO_TICKERS) * MINIMUM_ALLOCATION > 1:
        errors.append(
            f"Impossible to satisfy minimum allocation: "
            f"{len(PORTFOLIO_TICKERS)} stocks × {MINIMUM_ALLOCATION} = "
            f"{len(PORTFOLIO_TICKERS) * MINIMUM_ALLOCATION} > 1.0"
        )
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))
    
    return True
validate_settings()
