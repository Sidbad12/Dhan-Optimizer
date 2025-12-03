# Dhan Optimizer - Prophet Forecasting for Portfolio Optimisation

## Project Overview
An end-to-end machine learning project that forecasts Indian stock prices using Facebook/Meta Prophet time series forecasting model, then applies Markowitz portfolio optimisation to rebalance portfolios based on these forecasts.

**Built for Indian Stock Market (NSE)** - Optimized for top Indian stocks including Reliance, TCS, HDFC Bank, Infosys, and more.

_(This is for educational and illustrative purposes only - not financial advice)._

**Live Application**: Hosted on Hostinger VPS, runs daily at 9am UTC
- **Dashboard**: Modern, interactive portfolio analytics dashboard
- **Features**: Real-time predictions, performance tracking, correlation analysis


---

## 🎯 Key Features

### 📊 **Enhanced Streamlit Dashboard**
- **Professional Design**: Custom Chonburi + Domine font pairing
- **Full-Width Layout**: Sidebar removed for maximum screen space
- **Interactive Visualizations**:
  - Portfolio allocation treemap (colored by expected returns)
  - Sunburst chart for hierarchical allocation view
  - Performance comparison charts (predicted vs actual)
  - Correlation heatmap for diversification analysis
  - Cumulative return tracking
  - Prediction accuracy gauge charts

### 🤖 **AI-Powered Predictions**
- Prophet time series forecasting with Indian market holidays
- One-step-ahead price predictions
- Expected return calculations
- Historical performance tracking

### 📈 **Portfolio Analytics**
- **Key Metrics Dashboard**:
  - Expected portfolio return
  - Prediction accuracy (MAPE-based)
  - Active holdings count
  - Diversification score (1 - Herfindahl index)
- **Stock-wise Analysis**:
  - Individual stock performance
  - Error distribution analysis
  - Historical trend visualization

### 🔄 **Automated Workflows**
- Daily optimization runs via GitHub Actions
- Automatic data storage in Supabase
- Historical data backfilling support
- CircleCI integration for CI/CD

---

## Components

### 1. Prophet (Time Series Forecasting)

**What is Prophet?**

Prophet is Facebook's open-source time series forecasting tool designed for business forecasting. It handles trends, seasonality, and holidays automatically, making it robust and easy to use for forecasting time series data.

**How It Works in This Project:**

- **Input**: Historical NSE stock prices with datetime index
- **Model**: Prophet fits additive components (trend, seasonality, Indian holidays)
- **Output**: Forecasted prices for each asset for the next trading day
- **Training**: Fits to 2+ years of historical price data
- **Indian Market Support**: Includes NSE trading holidays (Diwali, Holi, Republic Day, etc.)

### 2. Markowitz Portfolio Optimisation

**What is Markowitz Portfolio Optimisation?**

Markowitz portfolio optimisation, also known as Modern Portfolio Theory (MPT), is a mathematical framework for constructing optimal portfolios. Developed by Harry Markowitz in 1952, it balances the trade-off between expected returns and risk.

**Key Concepts:**

- **Expected Return**: The weighted average of expected returns of individual assets
- **Risk (Volatility)**: Measured as the standard deviation of portfolio returns
- **Correlation**: How assets move relative to each other
- **Efficient Frontier**: The set of optimal portfolios offering the highest expected return for a given level of risk

**The Optimisation Problem:**

```
Maximize: μᵀw - λ(wᵀΣw)

Subject to:
- Σwᵢ = 1 (weights sum to 1)
- 0.05 ≤ wᵢ ≤ 0.30 (5% min, 30% max per stock)
- Additional constraints (sector limits, diversification)
```

Where:
- `μ` = vector of expected returns (from Prophet price forecasts)
- `Σ` = covariance matrix of asset returns (252-day lookback)
- `w` = portfolio weights
- `λ` = risk aversion parameter (default: 3.0, configurable in `src/settings.py`)

**How It Works in This Project:**

1. **Input**: Forecasted returns (derived from Prophet price predictions) for each NSE stock
2. **Risk Estimation**: Historical covariance matrix calculated from 1-year of returns
3. **Optimisation**: Solves for optimal weights using SciPy's SLSQP solver
4. **Constraints**: 5-30% allocation per stock, weights sum to 100%
5. **Output**: Optimal portfolio allocation balancing risk and return
6. **Rebalancing**: Portfolio weights updated daily based on new predictions

---

## Project Workflow

```
Historical Data Extraction (yfinance)
    ↓
Data Preprocessing & Alignment
    ↓
Prophet Model Training (with NSE holidays)
    ↓
Price Forecasting (Next Day)
    ↓
Markowitz Optimisation (Mean-Variance)
    ↓
Optimal Portfolio Weights
    ↓
Results Saved to Supabase
    ↓
Enhanced Streamlit Dashboard (Hosted on VPS)
```

---

## Installation

### Requirements

- **Python 3.12+**
  - Install via [PyEnv](https://github.com/pyenv/pyenv)
  - PyEnv can be installed via [Homebrew](https://brew.sh/)
- **Poetry** (dependency management)
  - [Installation guide](https://python-poetry.org/docs/basic-usage/)
- **Supabase Account** (database)
  - [Getting started guide](https://supabase.com/docs/guides/getting-started)
  - Create a `portfolio_predictions` table (schema below)
- **Optional**: CircleCI account for CI/CD
  - [Setup guide](https://circleci.com/blog/setting-up-continuous-integration-with-github/)

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Dhan-Optimizer.git
cd Dhan-Optimizer

# Install dependencies using Poetry
make install-dev

# Or manually
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env and add your Supabase credentials
```

### Supabase Table Schema

Create a table named `portfolio_predictions` with the following schema:

```sql
CREATE TABLE portfolio_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    as_of_date DATE NOT NULL,
    ticker TEXT NOT NULL,
    predicted_price NUMERIC NOT NULL,
    predicted_return NUMERIC NOT NULL,
    actual_prices_last_month JSONB,
    portfolio_weight NUMERIC NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_portfolio_predictions_date ON portfolio_predictions(as_of_date DESC);
CREATE INDEX idx_portfolio_predictions_ticker ON portfolio_predictions(ticker);
```

---

## Usage

### Basic Usage

Run portfolio optimization for current date:

```bash
poetry run python -m src.main
```

Or using the Makefile:

```bash
make run
```

This will:
1. Fetch historical data for configured tickers
2. Train Prophet models on each stock
3. Generate next-day price predictions
4. Optimize portfolio weights
5. Save results to Supabase

### Running the Enhanced Dashboard

Launch the interactive Streamlit dashboard:

```bash
poetry run streamlit run src/streamlit_app.py
```

Or using the Makefile:

```bash
make dashboard
```

**Dashboard Features:**
- 📅 **Date Selector**: View predictions for any historical date
- 📊 **Portfolio Metrics**: Expected return, accuracy, holdings, diversification
- 🥧 **Allocation Treemap**: Visual portfolio breakdown colored by expected returns
- 💹 **Sunburst Chart**: Hierarchical allocation view
- 📈 **Performance Charts**: Predicted vs actual prices with error analysis
- 🔗 **Correlation Matrix**: Stock correlation heatmap
- 📉 **Historical Trends**: Cumulative portfolio return over time

### Backfilling Historical Data

Populate Supabase with historical predictions:

```bash
# Backfill last 10 trading days (default)
poetry run python -m src.backfill_historical_data

# Backfill custom number of days
poetry run python -m src.backfill_historical_data --days 30
```

This is useful when:
- Setting up the dashboard for the first time
- You want to see historical trends
- Building performance tracking data

---

## Configuration

Edit `src/settings.py` to customize:

### Portfolio Configuration

```python
# Indian Stock Tickers (NSE)
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
```

### Optimization Parameters

```python
# Risk aversion (1-5, higher = more conservative)
RISK_AVERSION = 3.0

# Min/Max allocation per stock
MINIMUM_ALLOCATION = 0.05  # 5% minimum
MAXIMUM_ALLOCATION = 0.30  # 30% maximum

# Historical data range
START_DATE = "2023-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")
```

### Prophet Parameters

```python
PROPHET_PARAMS = {
    'daily_seasonality': True,
    'weekly_seasonality': True,
    'yearly_seasonality': True,
    'changepoint_prior_scale': 0.05,
    'seasonality_prior_scale': 10,
}
```

---

## Programmatic Usage

```python
from src.main import run_optimisation

# Run optimization for specific tickers and date range
result = run_optimisation(
    tickers=["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Access results
print(f"Date: {result['date']}")
print(f"Optimal Weights: {result['weights']}")
print(f"Predicted Returns: {result['predicted_returns']}")
print(f"Predicted Prices: {result['predictions']}")

# Example output:
# Date: 2024-12-31
# Optimal Weights: {'RELIANCE.NS': 0.25, 'TCS.NS': 0.40, 'HDFCBANK.NS': 0.35}
# Predicted Returns: {'RELIANCE.NS': 0.0123, 'TCS.NS': 0.0089, 'HDFCBANK.NS': 0.0156}
# Predicted Prices: {'RELIANCE.NS': 2567.80, 'TCS.NS': 3890.50, 'HDFCBANK.NS': 1678.90}
```

---

## Deployment

### GitHub Actions Workflows

**1. Daily Optimization** (`.github/workflows/daily-optimisation.yml`)
- Runs every day at 9:00 AM UTC
- Automatically fetches data, runs optimization, saves to Supabase
- Can be manually triggered from GitHub UI

**2. VPS Deployment** (`.github/workflows/deploy.yml`)
- Deploys to Hostinger VPS on push to `main` branch
- Automatically restarts Streamlit service
- Pulls latest code and installs dependencies

### Deploying to Hostinger VPS

1. **Set up VPS**:
   ```bash
   # SSH into your VPS
   ssh root@your-vps-ip
   
   # Clone repository
   cd /root
   git clone https://github.com/yourusername/Dhan-Optimizer.git
   cd Dhan-Optimizer
   
   # Install dependencies
   poetry install
   ```

2. **Create Systemd Service**:
   ```bash
   sudo nano /etc/systemd/system/streamlit-app.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Dhan Optimizer Streamlit Dashboard
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/Dhan-Optimizer
   Environment="PATH=/root/.local/bin:/usr/local/bin:/usr/bin:/bin"
   ExecStart=/root/.local/bin/poetry run streamlit run src/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start Service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable streamlit-app.service
   sudo systemctl start streamlit-app.service
   ```

4. **Set up Nginx Reverse Proxy**:
   ```bash
   sudo nano /etc/nginx/sites-available/dhan-optimizer
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

5. **Add GitHub Secrets**:
   - `SSH_PRIVATE_KEY`: Your VPS SSH private key
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key

---

## Development

### Code Quality Tools

```bash
# Linting
make lint

# Code formatting
make format

# Type checking
make type-check

# Run tests
make test

# Run all checks
make check

# Clean cache files
make clean
```

### Project Structure

```
Dhan-Optimizer/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main optimization entry point
│   ├── streamlit_app.py           # Enhanced dashboard
│   ├── extractor.py               # Data extraction from yfinance
│   ├── model.py                   # Prophet forecasting model
│   ├── optimiser.py               # Markowitz optimization
│   ├── processor.py               # Data preprocessing
│   ├── database.py                # Supabase operations
│   ├── settings.py                # Configuration
│   └── backfill_historical_data.py # Historical data loader
├── tests/
│   ├── test_extractor.py
│   ├── test_model.py
│   ├── test_optimiser.py
│   ├── test_processor.py
│   └── test_database.py
├── .github/workflows/
│   ├── daily-optimisation.yml     # Daily automation
│   └── deploy.yml                 # VPS deployment
├── .circleci/
│   └── config.yml                 # CI/CD pipeline
├── scripts/
│   └── deploy.sh                  # Deployment script
├── pyproject.toml                 # Dependencies & config
├── Makefile                       # Command shortcuts
└── README.md                      # This file
```

---

## Dashboard Screenshots

### Portfolio Overview
- Treemap showing allocation by weight and colored by expected return
- Sunburst chart for hierarchical portfolio view
- Holdings table with progress bars

### Stock Analysis
- Individual stock metrics (current price, predicted price, expected return)
- Performance comparison chart (predicted vs actual)
- Error analysis over time

### Performance Tab
- Prediction accuracy gauge
- Error distribution histogram
- Stock-wise performance table

### Advanced Analytics
- Correlation heatmap for diversification analysis
- Cumulative portfolio return chart
- Historical trend visualization

---

## Technical Details

### Indian Market Support
- **Holidays**: NSE trading holidays (2024-2025) included
- **Market Hours**: 9:15 AM - 3:30 PM IST
- **Currency**: Indian Rupees (₹)
- **Timezone**: Asia/Kolkata

### Performance Metrics
- **MAPE**: Mean Absolute Percentage Error
- **MAE**: Mean Absolute Error
- **Prediction Accuracy**: 100% - MAPE
- **Herfindahl Index**: Portfolio concentration measure

### Data Sources
- **Stock Data**: Yahoo Finance (yfinance) for NSE stocks
- **Database**: Supabase (PostgreSQL)
- **Caching**: Streamlit cache with 5-minute TTL

---

## Troubleshooting

### Common Issues

**1. Supabase Connection Error**
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Make sure .env file exists
cp .env.example .env
```

**2. Missing Dependencies**
```bash
# Reinstall all dependencies
poetry install --no-cache
```

**3. Prophet Installation Issues**
```bash
# Install system dependencies (macOS)
brew install gcc

# Or for Linux
sudo apt-get install build-essential
```

**4. Dashboard Not Loading**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart with debugging
poetry run streamlit run src/streamlit_app.py --logger.level=debug
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Run `make check` before committing

---

## License

This project is for educational purposes. Please refer to individual data source licenses:
- Yahoo Finance data subject to their terms of use
- Prophet by Meta (MIT License)
- Other dependencies as per their respective licenses

---

## Acknowledgments

- **Prophet**: Facebook/Meta's time series forecasting tool
- **Markowitz Theory**: Harry Markowitz's Modern Portfolio Theory
- **Indian Market Data**: Yahoo Finance
- **Hosting**: Hostinger VPS
- **Database**: Supabase

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Dhan-Optimizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Dhan-Optimizer/discussions)
- **Email**: your-email@example.com

---

## Disclaimer

⚠️ **Important**: This tool is for educational and research purposes only. It is NOT financial advice. Do not use this for actual trading decisions without proper due diligence and consultation with a qualified financial advisor. Past performance does not guarantee future results.

---

**Made with ❤️ for the Indian Stock Market**