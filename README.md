# Dhan Optimizer - AI-Powered Indian Stock Portfolio Manager

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://dhan-optimizer-z2x2wydkaappmrr7eampdnr.streamlit.app)
[![Daily Updates](https://img.shields.io/badge/Updates-Automated-00C853?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/Sidbad12/Dhan-Optimizer/actions)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

> **Fully automated ML pipeline** that forecasts Indian stock prices (NSE) using Facebook Prophet and optimizes portfolio allocation using Modern Portfolio Theory. Runs daily with predictions automatically updated at 4 PM IST.

🔗 **[View Live Dashboard](https://dhan-optimizer-z2x2wydkaappmrr7eampdnr.streamlit.app)** 

---

## Overview

An end-to-end machine learning project adapted for the **Indian Stock Market (NSE)** that combines:
-  **Prophet Time-Series Forecasting** - Next-day price predictions with Indian market holidays
- **Markowitz Portfolio Optimization** - Risk-adjusted allocation using Modern Portfolio Theory
-  **Automated Workflow** - Daily predictions via GitHub Actions at 4 PM IST
- **Live Dashboard** - Real-time visualization on Streamlit Cloud (99.9% uptime)
- **Production Database** - PostgreSQL backend via Supabase

**Built for Indian investors, students, and ML enthusiasts.** _(Educational purposes only - not financial advice)_

> **Note**: This project is forked from [egorhowell/Prophet-Forecasting-For-Portfolio-Optimisation](https://github.com/egorhowell/Prophet-Forecasting-For-Portfolio-Optimisation) and adapted for the Indian stock market with NSE tickers, Indian holidays, and INR currency.

---

## Key Features

###  What Makes This Special

- **Indian Market Ready**: NSE stock support with 31 Indian trading holidays (Diwali, Holi, etc.)
- **Real Portfolio**: 10 diversified Indian stocks across sectors (Banking, IT, FMCG, Telecom, Infrastructure)
- **Fully Automated**: GitHub Actions runs optimization daily at 4 PM IST after market close
- **Production Dashboard**: Always-on Streamlit Cloud deployment with historical trends
- **Smart Constraints**: 5-30% allocation limits per stock for proper diversification
- **Performance Tracking**: Historical prediction accuracy with predicted vs actual comparisons
- **CI/CD Pipeline**: Automated testing, linting, and deployment

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            GitHub Actions (Automated Daily Cron)            │
│          Runs Mon-Fri at 10:30 UTC (4:00 PM IST)            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Extraction (Yahoo Finance)                │
│    Historical NSE stock prices with .NS ticker suffix       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Prophet Forecasting (Facebook/Meta Prophet)         │
│   • Indian market holidays (31 holidays integrated)         │
│   • Trend + Seasonality decomposition                       │
│   • Next-day price prediction per stock                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│      Markowitz Portfolio Optimizer (SciPy SLSQP)            │
│   • Objective: Maximize return - λ × variance               │
│   • Risk aversion: λ = 3.0 (configurable)                   │
│   • Constraints: 5% min, 30% max per stock                  │
│   • Historical covariance from 252-day window               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Supabase (PostgreSQL Database)                    │
│    Persistent storage with upsert for daily updates         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Streamlit Cloud Dashboard                      │
│   • Portfolio weights (pie chart, treemap)                  │
│   • Historical trends (predicted vs actual)                 │
│   • Prediction accuracy metrics                             │
│   • Always-on with auto-wake from sleep                     │
└─────────────────────────────────────────────────────────────┘
```

---

##  Portfolio Composition

Diversified across major Indian sectors:

| Ticker | Company | Sector | Market Cap | Typical Allocation |
|--------|---------|--------|------------|-------------------|
| **RELIANCE.NS** | Reliance Industries | Energy & Petrochemicals | ₹17.5L Cr | 10-15% |
| **TCS.NS** | Tata Consultancy Services | IT Services | ₹13.8L Cr | 5-10% |
| **HDFCBANK.NS** | HDFC Bank | Private Banking | ₹12.2L Cr | 10-15% |
| **INFY.NS** | Infosys | IT Services | ₹6.5L Cr | 5-10% |
| **ICICIBANK.NS** | ICICI Bank | Private Banking | ₹9.8L Cr | 5-10% |
| **HINDUNILVR.NS** | Hindustan Unilever | FMCG | ₹6.2L Cr | 5-10% |
| **ITC.NS** | ITC Limited | FMCG & Tobacco | ₹5.1L Cr | 5-10% |
| **SBIN.NS** | State Bank of India | Public Sector Bank | ₹8.7L Cr | 15-20% |
| **BHARTIARTL.NS** | Bharti Airtel | Telecom | ₹12.5L Cr | 20-25% |
| **LT.NS** | Larsen & Toubro | Infrastructure | ₹5.6L Cr | 5-10% |

_Allocations rebalance daily based on predicted returns and risk optimization_

---

##  How It Works

### 1. Time-Series Forecasting (Prophet)

Facebook Prophet decomposes Indian stock prices into:
- **Trend**: Long-term price movement patterns
- **Seasonality**: Daily, weekly, and yearly cyclical patterns
- **Holidays**: 31 Indian market holidays (Republic Day, Diwali, Holi, etc.)
- **Uncertainty**: Prediction intervals (yhat_lower, yhat_upper)

```python
# Prophet configuration for Indian stocks
PROPHET_PARAMS = {
    'daily_seasonality': True,
    'weekly_seasonality': True,
    'yearly_seasonality': True,
    'changepoint_prior_scale': 0.05,  # Trend flexibility
    'seasonality_prior_scale': 10,     # Seasonality strength
}

# Indian market holidays included
INDIAN_MARKET_HOLIDAYS = [
    '2024-01-26',  # Republic Day
    '2024-11-01',  # Diwali
    # ... 29 more holidays
]
```

### 2. Portfolio Optimization (Markowitz)

Solves the **mean-variance optimization** problem:

```
Maximize: μᵀw - λ(wᵀΣw)

Subject to:
- Σwᵢ = 1              (weights sum to 100%)
- 0.05 ≤ wᵢ ≤ 0.30     (5% min, 30% max per stock)
```

Where:
- **μ** = Expected returns vector (from Prophet forecasts)
- **Σ** = Covariance matrix (252-day historical window)
- **w** = Portfolio weights (what we solve for)
- **λ** = Risk aversion parameter (3.0 = balanced, higher = more conservative)

**Result**: Optimal allocation that maximizes risk-adjusted returns

---

##  Quick Start

### Prerequisites

- **Python 3.12+** ([Install via pyenv](https://github.com/pyenv/pyenv))
- **Poetry** ([Installation guide](https://python-poetry.org/docs/#installation))
- **Supabase Account** (Free tier - [Sign up](https://supabase.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Dhan-Optimizer.git
cd Dhan-Optimizer

# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Add your Supabase credentials to .env:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your_anon_key_here
```

### Database Setup

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create new project
3. Go to SQL Editor → New Query
4. Run this SQL:

```sql
-- Create main table
CREATE TABLE portfolio_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    as_of_date DATE NOT NULL,
    ticker TEXT NOT NULL,
    predicted_price NUMERIC(10, 2),
    predicted_return NUMERIC(10, 4),
    actual_prices_last_month JSONB,
    portfolio_weight NUMERIC(10, 6),
    CONSTRAINT unique_prediction UNIQUE (as_of_date, ticker)
);

-- Create indexes
CREATE INDEX idx_as_of_date ON portfolio_predictions(as_of_date);
CREATE INDEX idx_ticker ON portfolio_predictions(ticker);

-- Enable RLS (Row Level Security)
ALTER TABLE portfolio_predictions ENABLE ROW LEVEL SECURITY;

-- Allow public read
CREATE POLICY "Allow public read" ON portfolio_predictions
    FOR SELECT USING (true);
```

### Run Optimization

```bash
# Run once manually
poetry run python -m src.main

# Or use Makefile
make run
```

**Expected output:**
```
Starting portfolio optimisation for tickers: ['RELIANCE.NS', ...] as of 2024-12-03
Extracting historical data...
Using 31 Indian trading holidays for Prophet model
RELIANCE.NS: Current ₹1546.30 → Predicted ₹1540.94 (Return: -0.35%)
TCS.NS: Current ₹3135.70 → Predicted ₹3143.49 (Return: 0.25%)
...
✅ Results successfully saved to Supabase database
```

### Launch Dashboard

```bash
# Start Streamlit dashboard locally
poetry run streamlit run src/streamlit_app.py

# Or use Makefile
make dashboard
```

Dashboard opens at: http://localhost:8501

---

##  Sample Results

### Portfolio Allocation (December 3, 2024)

```
BHARTIARTL.NS  ████████████████████████  23.89%  (Telecom)
SBIN.NS        ████████████████          15.90%  (Banking)
RELIANCE.NS    ███████████████           14.64%  (Energy)
HDFCBANK.NS    ████████████              12.43%  (Banking)
LT.NS          ████████                   8.15%  (Infrastructure)
TCS.NS         █████                      5.00%  (IT)
INFY.NS        █████                      5.00%  (IT)
ICICIBANK.NS   █████                      5.00%  (Banking)
HINDUNILVR.NS  █████                      5.00%  (FMCG)
ITC.NS         █████                      5.00%  (FMCG)
```

### Top Predictions

| Stock | Current | Predicted | Expected Return | Weight |
|-------|---------|-----------|----------------|--------|
| **HDFCBANK.NS** | ₹989.80 | ₹1,029.80 | **+4.04%**  | 12.43% |
| **SBIN.NS** | ₹967.30 | ₹991.56 | **+2.51%** | 15.90% |
| **LT.NS** | ₹4,030.50 | ₹4,124.82 | **+2.34%** | 8.15% |
| **ITC.NS** | ₹400.95 | ₹409.37 | **+2.10%** | 5.00% |
| **ICICIBANK.NS** | ₹1,373.00 | ₹1,385.36 | **+0.90%** | 5.00% |

---

## Configuration

### Portfolio Settings (`src/settings.py`)

```python
# Stock selection (NSE tickers)
PORTFOLIO_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", 
    "ICICIBANK.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS",
    "BHARTIARTL.NS", "LT.NS"
]

# Risk management
RISK_AVERSION = 3.0              # 1-5 (higher = more conservative)
MINIMUM_ALLOCATION = 0.05        # 5% minimum per stock
MAXIMUM_ALLOCATION = 0.30        # 30% maximum per stock

# Date range
START_DATE = "2023-01-01"        # Historical data start
END_DATE = datetime.now()        # Up to current date

# Market settings
MARKET_TIMEZONE = "Asia/Kolkata"
CURRENCY_SYMBOL = "₹"
MARKET_OPEN = "09:15"            # NSE opening time
MARKET_CLOSE = "15:30"           # NSE closing time
```

---

##  Automated Daily Updates

### GitHub Actions Setup

The project automatically runs every weekday at 4 PM IST:

1. **Add GitHub Secrets**:
   - Go to Settings → Secrets and variables → Actions
   - Add `SUPABASE_URL` and `SUPABASE_KEY`

2. **Workflow runs automatically**:
   - Monday to Friday at 10:30 UTC (4:00 PM IST)
   - After NSE market close (3:30 PM IST)
   - Saves predictions to Supabase
   - Dashboard updates automatically

3. **Manual trigger**:
   - Go to Actions tab
   - Select "Daily Portfolio Optimisation"
   - Click "Run workflow"

### Workflow File (`.github/workflows/daily-optimisation.yml`)

```yaml
name: Daily Portfolio Optimisation

on:
  schedule:
    - cron: '30 10 * * 1-5'  # 4:00 PM IST, Mon-Fri
  workflow_dispatch:          # Manual trigger

jobs:
  optimise:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Poetry
        uses: snok/install-poetry@v1
      - name: Install dependencies
        run: poetry install
      - name: Run optimization
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: poetry run python -m src.main
```

---

## Dashboard Features

### Main View
- **Date Selector**: Browse historical predictions
- **Portfolio Metrics**: 
  - Expected return
  - Number of holdings
  - Total portfolio weight
- **Pie Chart**: Visual allocation breakdown
- **Holdings Table**: Stock-by-stock breakdown with predictions

### Stock Analysis
- **Current vs Predicted Prices** (in ₹)
- **Expected Returns** (percentage)
-  **Historical Trends**: Predicted vs actual comparison
-  **Prediction Accuracy**: Error metrics

### Performance Tracking
-  **Trend Charts**: Multi-day prediction accuracy
- **Accuracy Metrics**: MAPE, MAE
-  **Error Analysis**: By stock and by date

---

##  Tech Stack

### Machine Learning & Data
- **Prophet** (1.2.1) - Time-series forecasting
- **NumPy** (1.26.4) - Numerical computing
- **Pandas** (2.3.3) - Data manipulation
- **SciPy** (1.16.3) - Optimization algorithms
- **Scikit-learn** (1.7.2) - ML utilities
- **yfinance** (0.2.66) - Yahoo Finance API

### Backend & Database
- **Python 3.12** - Core language
- **PostgreSQL** - Database (via Supabase)
- **Supabase** (2.24.0) - Backend-as-a-Service
- **Poetry** - Dependency management

### Frontend & Visualization
- **Streamlit** (1.51.0) - Interactive dashboard
- **Plotly** (6.5.0) - Interactive charts
- **Altair** (5.5.0) - Statistical visualizations

### DevOps & Infrastructure
- **GitHub Actions** - CI/CD automation
- **Streamlit Cloud** - Dashboard hosting
- **CircleCI** - Testing pipeline
- **python-dotenv** - Environment management

---

##  Testing

```bash
# Run all tests
poetry run pytest

# With coverage report
poetry run pytest --cov=src --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_model.py

# Code quality checks
make lint          # Ruff linting
make format        # Black formatting
make type-check    # Mypy type checking
make check         # All checks
```

---

## Project Structure

```
Dhan-Optimizer/
├── .github/
│   └── workflows/
│       └── daily-optimisation.yml    # Automated daily runs
├── src/
│   ├── main.py                       # Main optimization pipeline
│   ├── settings.py                   # Configuration (tickers, params)
│   ├── extractor.py                  # Yahoo Finance data fetching
│   ├── model.py                      # Prophet forecasting
│   ├── optimiser.py                  # Markowitz optimization
│   ├── processor.py                  # Data preprocessing
│   ├── database.py                   # Supabase operations
│   └── streamlit_app.py              # Dashboard UI
├── tests/                            # Unit tests
│   ├── test_extractor.py
│   ├── test_model.py
│   ├── test_optimiser.py
│   └── test_database.py
├── backfill_historical_data.py       # Backfill script
├── check_data.py                     # Data verification
├── test_supabase.py                  # Supabase test
├── pyproject.toml                    # Poetry dependencies
├── Makefile                          # Command shortcuts
└── README.md
```

---

## Backfilling Historical Data

Want to see trends immediately? Backfill the last 10 days:

```bash
# Backfill last 10 trading days (default)
poetry run python backfill_historical_data.py

# Custom number of days
poetry run python backfill_historical_data.py --days 20
```

**What it does:**
- Runs optimization for past N trading days
- Saves all predictions to Supabase
- Enables historical trend analysis
- Populates dashboard with data

**Note**: Takes ~3-5 minutes for 10 days (Prophet trains model for each day)

---

##  Deployment

### Streamlit Cloud (Current Deployment)

1. **Fork repository** on GitHub
2. **Sign up** at [share.streamlit.io](https://share.streamlit.io)
3. **Deploy**:
   - Click "New app"
   - Select your repo
   - Main file: `src/streamlit_app.py`
   - Python version: 3.12
4. **Add secrets** (Settings → Secrets):
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your_anon_key"
   ```
5. **Deploy** → App goes live!

**Result**: Always-on dashboard at your Streamlit URL

---

##  Educational Value

### What You Learn

1. **Time-Series Forecasting**
   - Prophet model architecture
   - Handling seasonality and holidays
   - Model tuning and validation

2. **Portfolio Theory**
   - Modern Portfolio Theory (Markowitz)
   - Mean-variance optimization
   - Risk-return tradeoff
   - Diversification strategies

3. **Production ML**
   - End-to-end pipeline design
   - Automated retraining
   - Model monitoring
   - Data storage and retrieval

4. **DevOps & Cloud**
   - CI/CD with GitHub Actions
   - Cloud deployment (Streamlit)
   - Database integration (Supabase)
   - Scheduled tasks (cron)

5. **Full-Stack Development**
   - Backend (Python, PostgreSQL)
   - Frontend (Streamlit, Plotly)
   - API integration (Yahoo Finance)
   - Testing and quality assurance

---

##  Disclaimer

**IMPORTANT - READ CAREFULLY**

This project is for **educational and research purposes only**:

-  **NOT financial advice** - Do not use for actual trading
-  **NO guarantees** - Past performance ≠ future results
-  **High risk** - Stock markets are inherently risky
-  **Consult professionals** - Always seek qualified financial advice

**Legal**: The author is not responsible for any financial losses. Use at your own risk.

---

## Credits & Attribution

### Original Project
This project is forked from **[egorhowell/Prophet-Forecasting-For-Portfolio-Optimisation](https://github.com/egorhowell/Prophet-Forecasting-For-Portfolio-Optimisation)**

**Major adaptations for Indian market:**
- ✅ NSE stock tickers (.NS suffix)
- ✅ Indian market holidays (31 holidays)
- ✅ Currency formatting (₹ INR)
- ✅ IST timezone handling
- ✅ Updated documentation

### Technologies
- **Facebook Prophet** - Robust time-series forecasting
- **Harry Markowitz** - Modern Portfolio Theory (Nobel Prize 1990)
- **Yahoo Finance** - Stock market data
- **Streamlit** - Beautiful dashboard framework
- **Supabase** - Excellent PostgreSQL backend

---

##  Contact & Support

- **Live Dashboard**: [dhan-optimizer.streamlit.app](https://dhan-optimizer-z2x2wydkaappmrr7eampdnr.streamlit.app)
- **GitHub Issues**: [Report bugs](https://github.com/Sidbad12/Dhan-Optimizer/issues)
- **GitHub Repo**: [Source code](https://github.com/Sidbad12/Dhan-Optimizer)

---

##  License

This project is for educational purposes. Please refer to:
- Original project: [Prophet-Forecasting-For-Portfolio-Optimisation](https://github.com/egorhowell/Prophet-Forecasting-For-Portfolio-Optimisation)
- Prophet: MIT License (Meta)
- Data sources: Subject to their respective terms

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

**Made with ❤️ for Indian investors and ML enthusiasts 🇮🇳**

[![GitHub stars](https://img.shields.io/github/stars/Sidbad12/Dhan-Optimizer?style=social)](https://github.com/Sidbad12/Dhan-Optimizer/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Sidbad12/Dhan-Optimizer?style=social)](https://github.com/Sidbad12/Dhan-Optimizer/network/members)

</div>
