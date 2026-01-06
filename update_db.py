# update_db.py - Run the scheduler once and update the database
import subprocess
import time
import os
from datetime import datetime
import sqlite3

def run_scheduler_once():
    """Run the scheduler one time to update the database"""
    print(f"Starting database update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Import and run the scheduler logic directly
    from scheduler_v2 import TradingSignalGenerator
    
    generator = TradingSignalGenerator()
    
    # Run signal generation once
    print("Generating signals for all symbols...")
    all_signals, strong_signals = generator.run(send_telegram=False)
    
    if all_signals:
        print(f"✓ Successfully updated {len(all_signals)} symbols")
        print(f"✓ Found {len(strong_signals)} strong signals")
        
        # Add a metadata entry about when the database was last updated
        add_update_metadata()
        
        return True
    else:
        print("✗ Failed to generate signals")
        return False

def add_update_metadata():
    """Add metadata about when the database was last updated"""
    try:
        conn = sqlite3.connect('trading_signals.db')
        cursor = conn.cursor()
        
        # Create metadata table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_metadata (
                id INTEGER PRIMARY KEY,
                last_updated TIMESTAMP,
                total_symbols INTEGER,
                last_update_status TEXT
            )
        ''')
        
        # Count total symbols in database
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM trading_signals")
        total_symbols = cursor.fetchone()[0]
        
        # Update or insert metadata
        cursor.execute('''
            INSERT OR REPLACE INTO dashboard_metadata 
            (id, last_updated, total_symbols, last_update_status)
            VALUES (1, ?, ?, ?)
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), total_symbols, 'success'))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Metadata updated: {total_symbols} symbols in database")
        
    except Exception as e:
        print(f"✗ Error updating metadata: {e}")

def check_database_health():
    """Check if the database has valid data"""
    try:
        conn = sqlite3.connect('trading_signals.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        tables = ['trading_signals', 'fibonacci_1h', 'polynomial_regression_daily', 'hvts_forecast']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"✗ Missing table: {table}")
                return False
        
        # Check if we have data
        cursor.execute("SELECT COUNT(*) FROM trading_signals")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        if count > 0:
            print(f"✓ Database health check passed: {count} signals found")
            return True
        else:
            print("✗ Database is empty")
            return False
            
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def main():
    """Main function to update the database"""
    print("=" * 60)
    print("TRADING SIGNALS DATABASE UPDATER")
    print("=" * 60)
    
    # Check current database health
    if os.path.exists('trading_signals.db'):
        print("\nChecking existing database...")
        if check_database_health():
            print("✓ Existing database is healthy")
        else:
            print("✗ Existing database has issues")
    
    # Run the update
    print("\nUpdating database...")
    success = run_scheduler_once()
    
    if success:
        print("\n" + "=" * 60)
        print("DATABASE UPDATE COMPLETE ✓")
        print("=" * 60)
        
        # Show summary
        conn = sqlite3.connect('trading_signals.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT last_updated, total_symbols FROM dashboard_metadata WHERE id = 1")
        metadata = cursor.fetchone()
        
        if metadata:
            print(f"\n📊 Database Summary:")
            print(f"   Last Updated: {metadata[0]}")
            print(f"   Total Symbols: {metadata[1]}")
        
        # Show signal distribution
        cursor.execute("""
            SELECT overall_signal, COUNT(*) as count 
            FROM trading_signals 
            GROUP BY overall_signal 
            ORDER BY count DESC
        """)
        
        print(f"\n📈 Signal Distribution:")
        for signal_type, count in cursor.fetchall():
            print(f"   {signal_type}: {count}")
        
        conn.close()
        
        print("\n✅ Ready to commit to GitHub and deploy to Streamlit!")
    else:
        print("\n❌ Database update failed")

if __name__ == "__main__":
    main()