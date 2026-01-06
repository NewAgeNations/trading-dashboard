# setup.py - Setup script for new users
import os
import sys

def check_dependencies():
    """Check if all dependencies are installed"""
    required = ['streamlit', 'pandas', 'numpy', 'plotly', 'ccxt', 'requests']
    
    print("Checking dependencies...")
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} is missing")
            return False
    
    return True

def create_env_template():
    """Create a .env template file"""
    if not os.path.exists('.env'):
        with open('.env.template', 'w') as f:
            f.write("""# Trading Signals Configuration
# Get API keys from Gate.io
GATE_API_KEY=your_api_key_here
GATE_API_SECRET=your_api_secret_here

# Optional: Telegram notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Database path
DATABASE_PATH=trading_signals.db
""")
        print("✓ Created .env.template file")
        print("  → Copy to .env and add your API keys")
    else:
        print("✓ .env file already exists")

def main():
    print("=" * 60)
    print("TRADING SIGNALS DASHBOARD SETUP")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies. Install with:")
        print("   pip install -r requirements.txt")
        return
    
    # Create environment template
    create_env_template()
    
    # Check for database
    if os.path.exists('trading_signals.db'):
        print("\n✓ Found existing database")
        print("  You can update it with: python update_db.py")
    else:
        print("\n⚠️  No database found")
        print("  Run once to generate: python update_db.py")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE ✓")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Copy .env.template to .env and add your API keys")
    print("2. Update database: python update_db.py")
    print("3. Run dashboard: streamlit run app.py")
    print("4. Commit to GitHub: git add . && git commit -m 'Initial commit'")

if __name__ == "__main__":
    main()