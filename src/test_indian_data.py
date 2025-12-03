"""
Test script to verify Indian stock data availability from Yahoo Finance
"""
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict

def test_single_ticker(ticker: str, days: int = 30) -> Dict:
    """
    Test if ticker data is available
    
    Args:
        ticker: Stock ticker with .NS or .BO suffix
        days: Number of days of historical data to fetch
    
    Returns:
        Dictionary with test results
    """
    try:
        end = datetime.now()
        start = end - timedelta(days=days)
        
        data = yf.download(ticker, start=start, end=end, progress=False)
        
        if data.empty:
            return {
                'ticker': ticker,
                'status': 'FAIL',
                'message': 'No data available',
                'rows': 0,
                'latest_date': None
            }
        
        # Handle both single and multi-ticker dataframes
        close_price = None
        if 'Close' in data.columns:
            close_val = data['Close'].iloc[-1]
            # If it's a Series (multi-ticker), get the first value
            close_price = float(close_val.iloc[0] if hasattr(close_val, 'iloc') else close_val)
        
        return {
            'ticker': ticker,
            'status': 'SUCCESS',
            'message': 'Data available',
            'rows': len(data),
            'latest_date': data.index[-1].strftime('%Y-%m-%d'),
            'latest_close': close_price
        }
        
    except Exception as e:
        return {
            'ticker': ticker,
            'status': 'ERROR',
            'message': str(e),
            'rows': 0,
            'latest_date': None
        }

def test_multiple_tickers(tickers: List[str], days: int = 30) -> pd.DataFrame:
    """
    Test multiple tickers at once
    
    Args:
        tickers: List of stock tickers
        days: Number of days of historical data
    
    Returns:
        DataFrame with test results
    """
    results = []
    
    print(f"\n{'='*70}")
    print(f"Testing Indian Stock Data Availability")
    print(f"{'='*70}\n")
    
    for ticker in tickers:
        print(f"Testing {ticker}...", end=" ")
        result = test_single_ticker(ticker, days)
        results.append(result)
        
        # Print status with emoji
        if result['status'] == 'SUCCESS':
            close_str = f"₹{result['latest_close']:.2f}" if result['latest_close'] else "N/A"
            print(f"✅ {result['rows']} days | Latest: {result['latest_date']} | {close_str}")
        elif result['status'] == 'FAIL':
            print(f"❌ {result['message']}")
        else:
            print(f"⚠️  {result['message']}")
    
    df = pd.DataFrame(results)
    return df

def get_stock_info(ticker: str) -> Dict:
    """Get detailed information about a stock"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'ticker': ticker,
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'currency': info.get('currency', 'INR'),
        }
    except Exception as e:
        return {
            'ticker': ticker,
            'error': str(e)
        }

def main():
    """Main test function"""
    
    # Test tickers from settings
    from src.settings import PORTFOLIO_TICKERS
    
    # Run tests
    results_df = test_multiple_tickers(PORTFOLIO_TICKERS, days=60)
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total tickers tested: {len(results_df)}")
    print(f"✅ Successful: {(results_df['status'] == 'SUCCESS').sum()}")
    print(f"❌ Failed: {(results_df['status'] == 'FAIL').sum()}")
    print(f"⚠️  Errors: {(results_df['status'] == 'ERROR').sum()}")
    
    # Show failed tickers
    failed = results_df[results_df['status'] != 'SUCCESS']
    if not failed.empty:
        print(f"\n⚠️  Failed Tickers:")
        for _, row in failed.iterrows():
            print(f"   - {row['ticker']}: {row['message']}")
    
    # Additional test: Fetch data for all tickers at once
    print(f"\n{'='*70}")
    print("Testing Batch Download")
    print(f"{'='*70}\n")
    
    try:
        end = datetime.now()
        start = end - timedelta(days=30)
        
        print(f"Downloading {len(PORTFOLIO_TICKERS)} tickers from {start.date()} to {end.date()}...")
        batch_data = yf.download(PORTFOLIO_TICKERS, start=start, end=end, group_by='ticker')
        
        if not batch_data.empty:
            print(f"✅ Batch download successful!")
            print(f"   Shape: {batch_data.shape}")
            print(f"   Date range: {batch_data.index[0].date()} to {batch_data.index[-1].date()}")
        else:
            print("❌ Batch download returned empty DataFrame")
            
    except Exception as e:
        print(f"❌ Batch download error: {e}")
    
    print(f"\n{'='*70}")
    print("Test Complete!")
    print(f"{'='*70}\n")
    
    return results_df

if __name__ == "__main__":
    main()