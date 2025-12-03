"""
Configuration settings for Indian Stock Portfolio Optimization
"""
from datetime import datetime, timedelta
import pandas as pd

# ==================== PORTFOLIO CONFIGURATION ====================

# Indian Stock Tickers (NSE)
# Top liquid stocks from different sectors for diversification
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

# Alternative: Nifty 50 Top 10
# PORTFOLIO_TICKERS = [
#     "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
#     "HINDUNILVR.NS", "ITC.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS"
# ]

# ==================== DATE RANGE ====================

# Historical data range
START_DATE = "2023-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

# For forecasting
FORECAST_PERIODS = 1  # Days ahead to forecast

# ==================== OPTIMIZATION PARAMETERS ====================

# Risk aversion parameter (lambda)
# Higher values = more conservative (lower risk)
# Lower values = more aggressive (higher returns)
# Typical range: 1-5
RISK_AVERSION = 3.0

# Minimum allocation per asset (to avoid too small positions)
# 0.05 = 5% minimum per stock
MINIMUM_ALLOCATION = 0.05

# Maximum allocation per asset (to ensure diversification)
# 0.30 = 30% maximum per stock
MAXIMUM_ALLOCATION = 0.30

# Allow short positions? (For Indian retail, typically False)
ALLOW_SHORT = False

# ==================== PROPHET MODEL PARAMETERS ====================

# Prophet model settings
PROPHET_PARAMS = {
    'daily_seasonality': True,
    'weekly_seasonality': True,
    'yearly_seasonality': True,
    'changepoint_prior_scale': 0.05,  # Flexibility of trend changes
    'seasonality_prior_scale': 10,     # Strength of seasonality
}

# ==================== INDIAN MARKET HOLIDAYS 2024-2025 ====================

# NSE Trading Holidays
INDIAN_MARKET_HOLIDAYS = pd.DataFrame({
    'holiday': 'indian_market_holiday',
    'ds': pd.to_datetime([
        # 2024 Holidays
        '2024-01-26',  # Republic Day
        '2024-03-08',  # Maha Shivaratri
        '2024-03-25',  # Holi
        '2024-03-29',  # Good Friday
        '2024-04-11',  # Id-Ul-Fitr
        '2024-04-17',  # Ram Navami
        '2024-04-21',  # Mahavir Jayanti
        '2024-05-01',  # Maharashtra Day
        '2024-05-23',  # Buddha Purnima
        '2024-06-17',  # Bakri Id
        '2024-07-17',  # Muharram
        '2024-08-15',  # Independence Day
        '2024-08-26',  # Janmashtami
        '2024-10-02',  # Gandhi Jayanti
        '2024-10-12',  # Dussehra
        '2024-11-01',  # Diwali (Laxmi Puja)
        '2024-11-02',  # Diwali Balipratipada
        '2024-11-15',  # Gurunanak Jayanti
        '2024-12-25',  # Christmas
        
        # 2025 Holidays (add as announced by NSE)
        '2025-01-26',  # Republic Day
        '2025-03-14',  # Holi
        '2025-03-31',  # Id-Ul-Fitr
        '2025-04-10',  # Mahavir Jayanti
        '2025-04-14',  # Dr. Ambedkar Jayanti
        '2025-04-18',  # Good Friday
        '2025-05-01',  # Maharashtra Day
        '2025-08-15',  # Independence Day
        '2025-10-02',  # Gandhi Jayanti
        '2025-10-21',  # Dussehra
        '2025-11-01',  # Diwali (Laxmi Puja)
        '2025-11-05',  # Gurunanak Jayanti
        '2025-12-25',  # Christmas
    ]),
    'lower_window': 0,
    'upper_window': 0,
})

# ==================== MARKET SETTINGS ====================

# Market timezone
MARKET_TIMEZONE = "Asia/Kolkata"

# Currency
CURRENCY_SYMBOL = "₹"
CURRENCY_CODE = "INR"

# Market hours (IST)
MARKET_OPEN = "09:15"   # 9:15 AM
MARKET_CLOSE = "15:30"  # 3:30 PM

# ==================== DATABASE CONFIGURATION ====================

# Supabase configuration (set these as environment variables)
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Table name for storing results
RESULTS_TABLE = "portfolio_predictions"

# ==================== LOGGING ====================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== VALIDATION ====================

# Add to the end of src/settings.py, before validate_settings()

# ==================== ADDITIONAL CONSTANTS ====================

# Supabase table name
SUPABASE_TABLE_NAME = RESULTS_TABLE  # Alias for compatibility

# Holiday name mapping (for compatibility with tests)
HOLIDAY_NAME_MAP = {}  # Not needed for Indian holidays, but keep for compatibility

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

# Validate on import
validate_settings()
