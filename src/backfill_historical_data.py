"""
Backfill script to populate Supabase with historical predictions
This will run the optimization for the last N days to build historical data
"""
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

from src.main import run_optimisation
from src.database import save_results_to_supabase
from src.settings import PORTFOLIO_TICKERS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def backfill_historical_predictions(days_back: int = 10):
    """
    Run optimization for the last N days to build historical data
    
    Args:
        days_back: Number of days to backfill (default: 10)
    """
    logger.info(f"Starting backfill for last {days_back} days...")
    logger.info(f"Portfolio tickers: {PORTFOLIO_TICKERS}")
    
    # Get market days (weekdays only)
    end_date = datetime.now()
    dates_to_process = []
    
    current_date = end_date
    while len(dates_to_process) < days_back:
        # Only include weekdays (Monday=0 to Friday=4)
        if current_date.weekday() < 5:  # Skip weekends
            dates_to_process.append(current_date)
        current_date -= timedelta(days=1)
    
    # Reverse to process oldest to newest
    dates_to_process.reverse()
    
    logger.info(f"Will process {len(dates_to_process)} trading days")
    
    successful_runs = 0
    failed_runs = 0
    
    for i, target_date in enumerate(dates_to_process, 1):
        date_str = target_date.strftime("%Y-%m-%d")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Processing day {i}/{len(dates_to_process)}: {date_str}")
        logger.info(f"{'='*70}")
        
        try:
            # Calculate start date for historical data (2 years back from target date)
            start_date = (target_date - timedelta(days=730)).strftime("%Y-%m-%d")
            
            # Run optimization as if we were on that date
            result = run_optimisation(
                tickers=PORTFOLIO_TICKERS,
                start_date=start_date,
                end_date=date_str
            )
            
            if not result:
                logger.warning(f"No result for {date_str} - likely no market data available")
                failed_runs += 1
                continue
            
            # Override the date to match our target date
            result["date"] = target_date.date()
            
            # Save to Supabase
            try:
                save_results_to_supabase(result)
                logger.info(f"✅ Successfully saved predictions for {date_str}")
                successful_runs += 1
            except Exception as db_error:
                logger.error(f"Failed to save {date_str} to Supabase: {db_error}")
                failed_runs += 1
                
        except Exception as e:
            logger.error(f"Error processing {date_str}: {e}")
            failed_runs += 1
            continue
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info("BACKFILL SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Total days attempted: {len(dates_to_process)}")
    logger.info(f"✅ Successful: {successful_runs}")
    logger.info(f"❌ Failed: {failed_runs}")
    logger.info(f"Success rate: {(successful_runs/len(dates_to_process)*100):.1f}%")
    logger.info(f"{'='*70}\n")
    
    if successful_runs > 0:
        logger.info("🎉 Backfill complete! You can now view trends in the dashboard:")
        logger.info("   poetry run streamlit run src/streamlit_app.py")
    else:
        logger.error("⚠️  No data was successfully saved. Check errors above.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backfill historical predictions")
    parser.add_argument(
        "--days",
        type=int,
        default=10,
        help="Number of days to backfill (default: 10)"
    )
    
    args = parser.parse_args()
    
    # Confirm with user
    print(f"\n{'='*70}")
    print("BACKFILL HISTORICAL PREDICTIONS")
    print(f"{'='*70}")
    print(f"This will run portfolio optimization for the last {args.days} trading days.")
    print(f"Tickers: {', '.join(PORTFOLIO_TICKERS)}")
    print(f"\nThis may take several minutes...")
    print(f"{'='*70}\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    backfill_historical_predictions(days_back=args.days)


if __name__ == "__main__":
    main()