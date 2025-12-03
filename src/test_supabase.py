"""
Test Supabase connection and database operations
"""
import os
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def test_connection():
    """Test basic Supabase connection"""
    print("="*70)
    print("Testing Supabase Connection")
    print("="*70)
    
    # Get credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in .env file")
        print("\nPlease ensure your .env file contains:")
        print("SUPABASE_URL=your_project_url")
        print("SUPABASE_KEY=your_anon_key")
        return False
    
    print(f"✓ Found SUPABASE_URL: {url[:30]}...")
    print(f"✓ Found SUPABASE_KEY: {key[:20]}...")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(url, key)
        print("✅ Successfully created Supabase client")
        
        # Test connection by checking if table exists
        response = supabase.table('portfolio_predictions').select("*").limit(1).execute()
        print("✅ Successfully connected to database")
        print(f"✓ Table 'portfolio_predictions' exists")
        
        return supabase
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def test_insert(supabase: Client):
    """Test inserting a sample record"""
    print("\n" + "="*70)
    print("Testing Insert Operation")
    print("="*70)
    
    # Sample data
    sample_data = {
        "prediction_date": date.today().isoformat(),
        "ticker": "RELIANCE.NS",
        "current_price": 2500.50,
        "predicted_price": 2520.75,
        "predicted_return": 0.81,
        "optimal_weight": 0.15,
        "model_version": "test_v1",
        "risk_aversion": 3.0
    }
    
    try:
        response = supabase.table('portfolio_predictions').insert(sample_data).execute()
        print("✅ Successfully inserted test record")
        print(f"✓ Record ID: {response.data[0]['id']}")
        return response.data[0]['id']
    except Exception as e:
        print(f"❌ Insert error: {e}")
        return None

def test_query(supabase: Client):
    """Test querying records"""
    print("\n" + "="*70)
    print("Testing Query Operation")
    print("="*70)
    
    try:
        # Query all records
        response = supabase.table('portfolio_predictions').select("*").execute()
        print(f"✅ Successfully queried database")
        print(f"✓ Total records: {len(response.data)}")
        
        if response.data:
            print("\nSample record:")
            record = response.data[0]
            print(f"  ID: {record['id']}")
            print(f"  Ticker: {record['ticker']}")
            print(f"  Date: {record['prediction_date']}")
            print(f"  Current Price: ₹{record['current_price']}")
            print(f"  Predicted Price: ₹{record['predicted_price']}")
            print(f"  Optimal Weight: {record['optimal_weight']*100:.2f}%")
        
        return True
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False

def test_update(supabase: Client, record_id: int):
    """Test updating a record"""
    print("\n" + "="*70)
    print("Testing Update Operation")
    print("="*70)
    
    try:
        # Update the test record with actual price
        update_data = {
            "actual_price": 2518.25,
            "actual_return": 0.71,
            "prediction_error": 0.10
        }
        
        response = supabase.table('portfolio_predictions')\
            .update(update_data)\
            .eq('id', record_id)\
            .execute()
        
        print("✅ Successfully updated record")
        print(f"✓ Updated record ID: {record_id}")
        return True
    except Exception as e:
        print(f"❌ Update error: {e}")
        return False

def test_views(supabase: Client):
    """Test database views"""
    print("\n" + "="*70)
    print("Testing Database Views")
    print("="*70)
    
    try:
        # Test latest_predictions view
        response = supabase.table('latest_predictions').select("*").execute()
        print(f"✅ latest_predictions view: {len(response.data)} records")
        
        # Test portfolio_summary view
        response = supabase.table('portfolio_summary').select("*").execute()
        print(f"✅ portfolio_summary view: {len(response.data)} records")
        
        return True
    except Exception as e:
        print(f"❌ View query error: {e}")
        return False

def cleanup_test_data(supabase: Client):
    """Clean up test data"""
    print("\n" + "="*70)
    print("Cleaning Up Test Data")
    print("="*70)
    
    try:
        response = supabase.table('portfolio_predictions')\
            .delete()\
            .eq('model_version', 'test_v1')\
            .execute()
        print("✅ Test data cleaned up")
        return True
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("🚀 Starting Supabase Tests")
    print("="*70)
    
    # Test 1: Connection
    supabase = test_connection()
    if not supabase:
        print("\n❌ Connection test failed. Please check your credentials.")
        return
    
    # Test 2: Insert
    record_id = test_insert(supabase)
    
    # Test 3: Query
    test_query(supabase)
    
    # Test 4: Update
    if record_id:
        test_update(supabase, record_id)
    
    # Test 5: Views
    test_views(supabase)
    
    # Cleanup
    cleanup_test_data(supabase)
    
    print("\n" + "="*70)
    print("✅ All Tests Complete!")
    print("="*70)
    print("\nYour Supabase setup is ready to use.")
    print("You can now run the portfolio optimization with:")
    print("  poetry run python -m src.main")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()