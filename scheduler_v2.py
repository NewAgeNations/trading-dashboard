# scheduler_v2.py - PRODUCTION VERSION FOR REAL TRADING DATA ONLY
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import time
import logging
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
import os
from dotenv import load_dotenv
import traceback
import sys

# Load environment variables from .env file
load_dotenv()

# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_emoji(emoji_name):
    """Get platform-appropriate emoji or text alternative"""
    if sys.platform == 'win32':
        emoji_map = {
            'key': '[KEY]',
            'chart': '[DATA]',
            'check': '[OK]',
            'cross': '[ERROR]',
            'warning': '[WARNING]',
            'clock': '[TIME]',
            'database': '[DB]',
            'rocket': '[ROCKET]',
            'signal': '[SIGNAL]',
            'star': '[STAR]',
            'hourglass': '[WAIT]',
            'info': '[INFO]',
            'magnify': '[SEARCH]',
            'list': '[LIST]',
            'bell': '[ALERT]',
            'money': '[MONEY]',
            'up': '[UP]',
            'down': '[DOWN]',
            'neutral': '[NEUTRAL]',
            'fire': '[FIRE]',
            'portfolio': '[PORTFOLIO]',
            'discount': '[DISCOUNT]',
            'overvalued': '[OVERVALUED]',
        }
        return emoji_map.get(emoji_name, '')
    else:
        emoji_map = {
            'key': '🔑',
            'chart': '📊',
            'check': '✅',
            'cross': '❌',
            'warning': '⚠️',
            'clock': '⏰',
            'database': '📁',
            'rocket': '🚀',
            'signal': '📈',
            'star': '⭐',
            'hourglass': '⏳',
            'info': 'ℹ️',
            'magnify': '🔍',
            'list': '📋',
            'bell': '🔔',
            'money': '💰',
            'up': '🟢',
            'down': '🔴',
            'neutral': '🟡',
            'fire': '🔥',
            'portfolio': '💼',
            'discount': '🔥',
            'overvalued': '⚠️',
        }
        return emoji_map.get(emoji_name, '')

# Configuration - loaded from environment variables
GATE_API_KEY = os.getenv('GATE_API_KEY')
GATE_API_SECRET = os.getenv('GATE_API_SECRET')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'trading_signals.db')

# Trading symbols - configurable via environment variable
DEFAULT_SYMBOLS = [
# 🚀 TOP-TIER BLUE-CHIP CRYPTOCURRENCIES
# 🏆 BLUE-CHIP LEADERS
"BTC/USDT:USDT", # 👑 Bitcoin
"ETH/USDT:USDT", # 🔷 Ethereum
"BNB/USDT:USDT", # 🟡 Binance Coin
"SOL/USDT:USDT", # ☀️ Solana
"XRP/USDT:USDT", # 💧 Ripple
"ADA/USDT:USDT", # 🔶 Cardano
"AVAX/USDT:USDT", # ❄️ Avalanche
"DOT/USDT:USDT", # 🔴 Polkadot
"DOGE/USDT:USDT", # 🐕 Dogecoin
"LINK/USDT:USDT", # 🔗 Chainlink

# 🌐 LAYER 1 & DEFI POWERHOUSES
"ATOM/USDT:USDT", # ⚛️ Cosmos
"NEAR/USDT:USDT", # 🌲 Near Protocol
"ALGO/USDT:USDT", # 🧩 Algorand
"VET/USDT:USDT", # 🚗 VeChain
"FIL/USDT:USDT", # 📁 Filecoin
"ICP/USDT:USDT", # 🌐 Internet Computer
"AAVE/USDT:USDT", # 👻 Aave
"XTZ/USDT:USDT", # 🏺 Tezos
"DASH/USDT:USDT", # 💨 Dash
"ZEC/USDT:USDT", # 🛡️ Zcash
"UNI/USDT:USDT", # 🦄 Uniswap
"CRV/USDT:USDT", # 📈 Curve DAO
"LDO/USDT:USDT", # 🚀 Lido DAO
"OP/USDT:USDT", # 🎭 Optimism
"SUI/USDT:USDT", # 💧 Sui

# 🚀 EMERGING & TRENDING GEMS
"APT/USDT:USDT", # 🏢 Aptos
"ARB/USDT:USDT", # ⚔️ Arbitrum
"SEI/USDT:USDT", # 🌊 Sei Network
"TIA/USDT:USDT", # 🎪 Celestia
"INJ/USDT:USDT", # 💉 Injective
"FET/USDT:USDT", # 🤖 Fetch.ai
"RUNE/USDT:USDT", # ⚡ THORChain
"IMX/USDT:USDT", # 🎮 Immutable X
"AR/USDT:USDT", # 🗃️ Arweave
"SAND/USDT:USDT", # 🏖️ The Sandbox
"MANA/USDT:USDT", # 🏙️ Decentraland
"APE/USDT:USDT", # 🦍 ApeCoin
"GMT/USDT:USDT", # 👟 STEPN
"GALA/USDT:USDT", # 🎮 Gala Games
"AXS/USDT:USDT", # 🛡️ Axie Infinity
"CHZ/USDT:USDT", # ⚽ Chiliz
"ENJ/USDT:USDT", # 🎴 Enjin Coin
"THETA/USDT:USDT", # 📹 Theta Network

# 😂 MEME COINS & CULTURE
"PEPE/USDT:USDT", # 🐸 Pepe
"FLOKI/USDT:USDT", # 🐕 Floki
"BONK/USDT:USDT", # 🐶 Bonk
"WIF/USDT:USDT", # 🧢 dogwifhat
"MEME/USDT:USDT", # 🎨 Memecoin
"SHIB/USDT:USDT", # 🐕 Shiba Inu

# 🤖 AI & EMERGING TECH
"NMR/USDT:USDT", # 🧠 Numeraire
"YGG/USDT:USDT", # 🎮 Yield Guild Games
"ILV/USDT:USDT", # 🏹 Illuvium
"MASK/USDT:USDT", # 🎭 Mask Network
"LPT/USDT:USDT", # 🎥 Livepeer
"LRC/USDT:USDT", # 🔄 Loopring

# 🎯 GATE.IO EXCLUSIVES & NEW LISTINGS
"LAB/USDT:USDT", # 🔬 LABS Group
"ICNT/USDT:USDT", # 🪙 Iconic Token
"PIPPIN/USDT:USDT", # 🍎 Pippin
"FHE/USDT:USDT", # 🔒 Fhenix
"COAI/USDT:USDT", # 🧠 COAI
"XPL/USDT:USDT", # 🚀 XPL
"PLUME/USDT:USDT", # 🌬️ Plume Network
"CC/USDT:USDT", # 🎨 CryptoCars
"ZORA/USDT:USDT", # 🎭 Zora
"PTB/USDT:USDT", # ⚙️ PTB
"ORDER/USDT:USDT", # 📜 Order
"MNT/USDT:USDT", # 🏔️ Mantle
"IR/USDT:USDT", # ⚡ IR
"BEAT/USDT:USDT", # 🎵 Beat
"VOOI/USDT:USDT", # 🍜 Vooi

# 📈 ADDITIONAL GATE.IO FAVORITES
"BAS/USDT:USDT", # 🧱 BAS
"ALPINE/USDT:USDT", # 🏎️ Alpine
"BANK/USDT:USDT", # 🏦 Bank
"BAN/USDT:USDT", # 🍌 Banano
"ASR/USDT:USDT", # 👑 AS Roma Fan Token
"KAS/USDT:USDT", # 💎 Kaspa
"ENA/USDT:USDT", # 🌀 Ethena
"AVNT/USDT:USDT", # 🎭 AVNT
"TRUMP/USDT:USDT", # 👔 Trump
"JUP/USDT:USDT", # 🪐 Jupiter
"PYTH/USDT:USDT", # 🐍 Pyth Network
"WLD/USDT:USDT", # 👁️ Worldcoin
"BLUR/USDT:USDT", # 🎨 Blur
"DYM/USDT:USDT", # 🌉 Dymension

# 💎 HIGH-VOLUME ALTS
"POL/USDT:USDT", # 🌐 Polygon
"HBAR/USDT:USDT", # ⚡ Hedera
"ZIL/USDT:USDT", # ⚡ Zilliqa
"ONT/USDT:USDT", # 🐉 Ontology
"IOTA/USDT:USDT", # 🔗 IOTA
"QTUM/USDT:USDT", # 💻 Qtum
"NEO/USDT:USDT", # 📱 NEO
"WAVES/USDT:USDT", # 🌊 Waves
"KAVA/USDT:USDT", # ☕ Kava
"ROSE/USDT:USDT", # 🌹 Oasis Network
"ONE/USDT:USDT", # 🔢 Harmony

# 🕰️ LEGACY & ORIGINAL TOKENS
"NIGHT/USDT:USDT", # 🌙 Night
"ANIME/USDT:USDT", # 🎌 Anime
"PIEVERSE/USDT:USDT", # 🥧 PieVerse
"CYS/USDT:USDT", # 🛡️ Cyclos
"STRK/USDT:USDT", # ⚡ Strike
"MON/USDT:USDT", # 👾 Monavale
"HYPE/USDT:USDT", # 🚀 Hype
"ASTER/USDT:USDT", # 🌼 Aster
"RAVE/USDT:USDT", # 🎧 Rave
"H/USDT:USDT", # ⚛️ Hydrogen
"PUMP/USDT:USDT", # 📈 Pump
"ARC/USDT:USDT", # 🏹 Arc
"STABLE/USDT:USDT", # ⚖️ Stable
"XPIN/USDT:USDT", # 📌 XPIN
"DGRAM/USDT:USDT", # 📸 DGram
"ATU/USDT:USDT", # 🌊 Atu
"LUMIA/USDT:USDT", # 💡 Lumia
"QU/USDT:USDT", # ❓ QU
"ACT/USDT:USDT", # 🎬 ACT
"NIL/USDT:USDT", # ❄️ NIL
"4/USDT:USDT", # 4️⃣ Four
"EPIC/USDT:USDT", # 🏹 Epic
"F/USDT:USDT", # ⚡ F
"LYN/USDT:USDT", # 🐺 LynKey
"US/USDT:USDT", # 🇺🇸 US
"TRUTH/USDT:USDT", # 🕊️ Truth
"RESOLV/USDT:USDT", # ✅ Resolv
"CUDIS/USDT:USDT", # 🌿 Cudis
"SOMI/USDT:USDT", # 🌟 Somi
"MMT/USDT:USDT", # 📊 MMT
"WET/USDT:USDT", # 💧 Wet
"ACE/USDT:USDT", # 🎮 Ace
"PLANCK/USDT:USDT", # 📐 Planck
"RIVER/USDT:USDT", # 🌊 River
"ME/USDT:USDT", # 👤 ME
"LIGHT/USDT:USDT" # 💡 Light

]

# Load symbols from environment or use defaults
SYMBOLS_ENV = os.getenv('TRADING_SYMBOLS')
if SYMBOLS_ENV:
    SYMBOLS = [s.strip() for s in SYMBOLS_ENV.split(',') if s.strip()]
else:
    SYMBOLS = DEFAULT_SYMBOLS

class TradingSignalGenerator:
    """Production signal generator for real trading data only"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the signal generator with API validation"""
        self.db_path = db_path or DATABASE_PATH
        
        # Validate API keys before initialization
        if not GATE_API_KEY or not GATE_API_SECRET:
            logger.error(f"{get_emoji('cross')} GATE_API_KEY and GATE_API_SECRET are required in .env file")
            logger.error("Please set these environment variables and try again.")
            raise ValueError("API keys are required for real trading data")
        
        self.exchange = None
        self.initialize_exchange()
        self.init_database()
    
    def initialize_exchange(self):
        """Initialize the Gate.io exchange connection with validation"""
        try:
            logger.info(f"{get_emoji('key')} Initializing Gate.io exchange connection...")
            
            self.exchange = ccxt.gateio({
                'apiKey': GATE_API_KEY,
                'secret': GATE_API_SECRET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                    'adjustForTimeDifference': True,
                },
                'timeout': 30000,
                'rateLimit': 1000,
            })
            
            # Test the connection with a lightweight API call
            logger.info("Testing exchange connection...")
            
            # Try a different API call since fetch_status() is not supported
            try:
                # Use fetch_time() which is more universally supported
                server_time = self.exchange.fetch_time()
                logger.info(f"Exchange connection successful (server time: {server_time})")
                
                # Verify API permissions
                try:
                    # Try to fetch ticker to verify API works
                    ticker = self.exchange.fetch_ticker('BTC/USDT')
                    logger.info(f"{get_emoji('check')} API connection successful. BTC/USDT price: {ticker.get('last', 'N/A')}")
                except Exception as e:
                    logger.warning(f"{get_emoji('warning')} Limited API permissions (may not affect data fetching): {str(e)}")
                    
            except Exception as e:
                # If fetch_time() also fails, try a simpler test
                logger.info(f"Using alternative connection test: {str(e)}")
                try:
                    markets = self.exchange.load_markets()
                    logger.info(f"{get_emoji('check')} Successfully loaded {len(markets)} markets")
                except Exception as e2:
                    logger.warning(f"{get_emoji('warning')} Could not load markets, but connection may still work: {str(e2)}")
            
        except ccxt.AuthenticationError:
            logger.error(f"{get_emoji('cross')} Authentication failed. Please check your API keys.")
            raise
        except ccxt.NetworkError:
            logger.error(f"{get_emoji('cross')} Network error. Please check your internet connection.")
            raise
        except Exception as e:
            logger.error(f"{get_emoji('cross')} Failed to initialize exchange: {str(e)}")
            raise
    
    def init_database(self):
        """Initialize SQLite database and create all tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            logger.info(f"{get_emoji('database')} Initializing database at: {self.db_path}")
            
            # Create dashboard_metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dashboard_metadata (
                    id INTEGER PRIMARY KEY,
                    last_updated TIMESTAMP,
                    total_symbols INTEGER,
                    last_update_status TEXT,
                    update_duration_seconds REAL,
                    data_source TEXT DEFAULT 'gateio'
                )
            ''')
            
            # Create hvts_forecast table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hvts_forecast (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    current_price REAL NOT NULL,
                    forecast_1d REAL NOT NULL,
                    forecast_7d REAL NOT NULL,
                    forecast_14d REAL NOT NULL,
                    forecast_30d REAL NOT NULL,
                    poly_signal TEXT NOT NULL,
                    poly_emoji TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp)
                )
            ''')
            
            # Create trading_signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    current_price REAL NOT NULL,
                    poly_1h_signal TEXT NOT NULL,
                    fib_15m_signal TEXT NOT NULL,
                    fib_signal TEXT NOT NULL,
                    poly_signal TEXT NOT NULL,
                    rsi_zone TEXT NOT NULL,
                    macd_signal TEXT NOT NULL,
                    pivot_zone TEXT NOT NULL,
                    overall_signal TEXT NOT NULL,
                    forecast_1h REAL,
                    forecast_1d REAL,
                    forecast_7d REAL,
                    forecast_14d REAL,
                    forecast_30d REAL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create fibonacci_1h table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fibonacci_1h (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    current_price REAL NOT NULL,
                    fib_level_0 REAL NOT NULL,
                    fib_level_23_6 REAL NOT NULL,
                    fib_level_38_2 REAL NOT NULL,
                    fib_level_50 REAL NOT NULL,
                    fib_level_61_8 REAL NOT NULL,
                    fib_level_78_6 REAL NOT NULL,
                    fib_level_100 REAL NOT NULL,
                    fib_level_127_2 REAL,
                    fib_level_161_8 REAL,
                    fib_level_261_8 REAL,
                    fib_level_423_6 REAL,
                    fib_1h_signal TEXT NOT NULL,
                    pivot_zone TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp)
                )
            ''')
            
            # Create polynomial_regression_daily table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS polynomial_regression_daily (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    current_price REAL NOT NULL,
                    poly_regression_value REAL NOT NULL,
                    poly_signal_daily TEXT NOT NULL,
                    poly_confidence REAL NOT NULL,
                    r_squared REAL NOT NULL,
                    trend_strength REAL NOT NULL,
                    support_level REAL NOT NULL,
                    resistance_level REAL NOT NULL,
                    forecast_1d REAL NOT NULL,
                    forecast_7d REAL NOT NULL,
                    forecast_30d REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp)
                )
            ''')
            
            # Create indices for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_symbol ON trading_signals(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON trading_signals(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fib_1h_symbol ON fibonacci_1h(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fib_1h_timestamp ON fibonacci_1h(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reg_symbol ON polynomial_regression_daily(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reg_timestamp ON polynomial_regression_daily(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hvts_symbol ON hvts_forecast(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hvts_timestamp ON hvts_forecast(timestamp)')
            
            conn.commit()
            conn.close()
            
            logger.info(f"{get_emoji('check')} Database initialization completed successfully")
            
        except Exception as e:
            logger.error(f"{get_emoji('cross')} Error initializing database: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def fetch_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch real OHLCV data from Gate.io"""
        if self.exchange is None:
            raise RuntimeError("Exchange not initialized")
        
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{max_retries}: Fetching {timeframe} data for {symbol}")
                
                # Clean symbol format for Gate.io
                # Gate.io futures symbols typically use format like "BTC/USDT:USDT"
                clean_symbol = symbol
                
                # Remove any duplicate USDT if present
                if symbol.endswith(':USDT') and '/USDT:' in symbol:
                    clean_symbol = symbol
                
                # Fetch OHLCV data
                ohlcv = self.exchange.fetch_ohlcv(clean_symbol, timeframe, limit=limit)
                
                if not ohlcv or len(ohlcv) == 0:
                    logger.warning(f"No data returned for {symbol} with timeframe {timeframe}")
                    return None
                
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # Validate data
                if df['close'].isnull().any():
                    logger.warning(f"NaN values found in {symbol} data, attempting to fill")
                    df = df.ffill().bfill()
                
                logger.info(f"{get_emoji('check')} Successfully fetched {len(df)} {timeframe} records for {symbol}")
                return df
                
            except ccxt.RateLimitExceeded:
                wait_time = retry_delay * (attempt + 1)
                logger.warning(f"Rate limit exceeded for {symbol}. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
                
            except ccxt.NetworkError as e:
                logger.warning(f"Network error for {symbol}: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
                
            except ccxt.ExchangeError as e:
                # Try alternative symbol format
                if "Invalid symbol" in str(e) and attempt == 0:
                    logger.warning(f"Invalid symbol {symbol}, trying alternative format...")
                    # Try spot format
                    spot_symbol = symbol.replace(':USDT', '')
                    try:
                        ohlcv = self.exchange.fetch_ohlcv(spot_symbol, timeframe, limit=limit)
                        if ohlcv and len(ohlcv) > 0:
                            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                            logger.info(f"{get_emoji('check')} Successfully fetched spot data for {spot_symbol}")
                            return df
                    except:
                        pass
                
                logger.error(f"Exchange error for {symbol}: {str(e)}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(retry_delay)
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error fetching data for {symbol}: {str(e)}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(retry_delay)
                continue
        
        return None
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index with validation"""
        try:
            if len(prices) < period + 1:
                logger.warning(f"Insufficient data for RSI calculation (needed: {period}, got: {len(prices)})")
                return pd.Series([50] * len(prices), index=prices.index)
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # Avoid division by zero
            rs = gain / loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            
            # Fill NaN values
            rsi = rsi.fillna(50)
            
            # Clip to valid range
            rsi = rsi.clip(0, 100)
            
            return rsi
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return pd.Series([50] * len(prices), index=prices.index)
    
    def calculate_macd(self, prices: pd.Series, fast_period: int = 12, 
                       slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator with validation"""
        try:
            if len(prices) < slow_period:
                logger.warning(f"Insufficient data for MACD (needed: {slow_period}, got: {len(prices)})")
                zeros = pd.Series([0] * len(prices), index=prices.index)
                return zeros, zeros, zeros
            
            # Calculate EMAs
            ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
            ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
            
            # MACD line
            macd_line = ema_fast - ema_slow
            
            # Signal line
            signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
            
            # MACD histogram
            macd_histogram = macd_line - signal_line
            
            return macd_line, signal_line, macd_histogram
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            zeros = pd.Series([0] * len(prices), index=prices.index)
            return zeros, zeros, zeros
    
    def get_macd_signal(self, macd_line: pd.Series, signal_line: pd.Series, 
                       macd_histogram: pd.Series) -> Tuple[str, str]:
        """Get MACD trading signal"""
        try:
            if len(macd_line) < 2:
                return "Neutral", get_emoji('neutral')
            
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            current_hist = macd_histogram.iloc[-1]
            prev_macd = macd_line.iloc[-2]
            prev_signal = signal_line.iloc[-2]
            prev_hist = macd_histogram.iloc[-2]
            
            # Bullish signals
            if current_macd > current_signal and prev_macd <= prev_signal:
                return "Bullish Crossover", get_emoji('up')
            elif current_hist > 0 and prev_hist <= 0:
                return "Bullish Momentum", get_emoji('up')
            elif current_macd > 0 and current_macd > current_signal:
                return "Bullish", get_emoji('up')
            
            # Bearish signals
            elif current_macd < current_signal and prev_macd >= prev_signal:
                return "Bearish Crossover", get_emoji('down')
            elif current_hist < 0 and prev_hist >= 0:
                return "Bearish Momentum", get_emoji('down')
            elif current_macd < 0 and current_macd < current_signal:
                return "Bearish", get_emoji('down')
            
            # Neutral
            else:
                return "Neutral", get_emoji('neutral')
                
        except Exception as e:
            logger.error(f"Error getting MACD signal: {str(e)}")
            return "Neutral", get_emoji('neutral')
    
    def polynomial_regression_forecast(self, df: pd.DataFrame, degree: int = 3, 
                                      periods: int = 30) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Generate polynomial regression forecast"""
        try:
            if len(df) < degree + 1:
                logger.warning(f"Insufficient data for polynomial regression (needed: {degree+1}, got: {len(df)})")
                return None, None
            
            x = np.arange(len(df))
            y = df['close'].values
            
            # Ensure we have valid data
            if len(np.unique(y)) < 2:
                logger.warning("Insufficient price variation for regression")
                return None, None
            
            # Perform polynomial regression
            coeffs = np.polyfit(x, y, degree)
            polynomial = np.poly1d(coeffs)
            
            # Generate forecast
            x_forecast = np.arange(len(df), len(df) + periods)
            y_forecast = polynomial(x_forecast)
            
            # Ensure forecast is reasonable (no negative prices)
            y_forecast = np.maximum(y_forecast, y[-1] * 0.1)  # Don't drop below 10% of current price
            
            return y_forecast, coeffs
            
        except Exception as e:
            logger.error(f"Error in polynomial regression: {str(e)}")
            return None, None
    
    def get_poly_signal_1h(self, df: pd.DataFrame, current_price: float) -> Tuple[str, str, float]:
        """Get 1-hour polynomial regression trend signal"""
        try:
            forecast, _ = self.polynomial_regression_forecast(df, degree=3, periods=5)
            
            if forecast is not None and len(forecast) >= 1:
                forecast_1 = forecast[0]
                
                # Determine trend based on forecast
                price_change_pct = ((forecast_1 - current_price) / current_price) * 100
                
                if price_change_pct > 0.5:  # 0.5% increase
                    return "Bullish", get_emoji('up'), forecast_1
                elif price_change_pct < -0.5:  # 0.5% decrease
                    return "Bearish", get_emoji('down'), forecast_1
                else:
                    return "Neutral", get_emoji('neutral'), forecast_1
            else:
                return "Neutral", get_emoji('neutral'), current_price
                
        except Exception as e:
            logger.error(f"Error in 1-hour polynomial signal: {str(e)}")
            return "Neutral", get_emoji('neutral'), current_price
    
    def calculate_fibonacci_levels(self, high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement and extension levels"""
        try:
            if high <= low:
                logger.warning(f"Invalid high/low values: high={high}, low={low}")
                high = max(high, low * 1.01)  # Ensure high > low
            
            diff = high - low
            
            levels = {
                '0%': high,
                '23.6%': high - diff * 0.236,
                '38.2%': high - diff * 0.382,
                '50%': high - diff * 0.5,
                '61.8%': high - diff * 0.618,
                '78.6%': high - diff * 0.786,
                '100%': low,
                '127.2%': low - diff * 0.272,
                '161.8%': low - diff * 0.618,
                '261.8%': low - diff * 1.618,
                '423.6%': low - diff * 3.236
            }
            
            return levels
            
        except Exception as e:
            logger.error(f"Error calculating Fibonacci levels: {str(e)}")
            return {'0%': high, '100%': low}
    
    def get_fibonacci_signal(self, current_price: float, fib_levels: Dict[str, float]) -> Tuple[str, str]:
        """Get Fibonacci-based signal"""
        try:
            if '61.8%' in fib_levels and '38.2%' in fib_levels:
                if current_price > fib_levels['61.8%']:
                    return "Bullish", get_emoji('up')
                elif current_price < fib_levels['38.2%']:
                    return "Bearish", get_emoji('down')
            
            return "Neutral", get_emoji('neutral')
            
        except Exception as e:
            logger.error(f"Error getting Fibonacci signal: {str(e)}")
            return "Neutral", get_emoji('neutral')
    
    def get_rsi_zone(self, rsi_value: float) -> Tuple[str, str]:
        """Get RSI zone"""
        try:
            if rsi_value < 30:
                return "Oversold", get_emoji('up')
            elif rsi_value < 40:
                return "Undervalued", get_emoji('up')
            elif rsi_value < 60:
                return "Neutral", get_emoji('neutral')
            elif rsi_value < 70:
                return "Overvalued", get_emoji('down')
            else:
                return "Overbought", get_emoji('down')
        except Exception as e:
            logger.error(f"Error getting RSI zone: {str(e)}")
            return "Neutral", get_emoji('neutral')
    
    def calculate_pivot_zones(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate precise pivot zones according to pseudocode specification"""
        try:
            # Use daily data for pivot zone calculation
            if len(df) < 20:
                recent_data = df
            else:
                recent_data = df.tail(20)  # Last 20 daily candles
            
            # Calculate recent high and low
            recent_low = float(recent_data['low'].min())
            recent_high = float(recent_data['high'].max())
            
            # Ensure we have a valid price range
            if recent_high <= recent_low:
                recent_high = recent_low * 1.05  # Add 5% margin if high <= low
            
            price_range = recent_high - recent_low
            
            # Calculate zones as percentages of range from recent_low
            zones = {
                'extreme_discount': recent_low + 0.1 * price_range,
                'accumulation_lower': recent_low + 0.1 * price_range,
                'accumulation_upper': recent_low + 0.3 * price_range,
                'reversal_zone': recent_low + 0.5 * price_range,
                'strong_support': recent_low + 0.7 * price_range,
                'recent_low': recent_low,
                'recent_high': recent_high,
                'price_range': price_range
            }
            
            # Calculate accumulation mid-range
            zones['accumulation_mid_range'] = (zones['accumulation_lower'] + zones['accumulation_upper']) / 2
            
            logger.debug(f"Pivot zones calculated:")
            logger.debug(f"  Recent Low: ${recent_low:.4f}, Recent High: ${recent_high:.4f}")
            logger.debug(f"  Extreme Discount: ${zones['extreme_discount']:.4f}")
            logger.debug(f"  Accumulation: ${zones['accumulation_lower']:.4f} - ${zones['accumulation_upper']:.4f}")
            logger.debug(f"  Reversal Zone: ${zones['reversal_zone']:.4f}")
            logger.debug(f"  Strong Support: ${zones['strong_support']:.4f}")
            
            return zones
            
        except Exception as e:
            logger.error(f"Error calculating pivot zones: {str(e)}")
            return {}
    
    def get_pivot_zone(self, current_price: float, pivot_levels: Dict[str, float]) -> Tuple[str, str, Dict[str, float]]:
        """Get current pivot zone with detailed zone information"""
        try:
            if not pivot_levels or 'extreme_discount' not in pivot_levels:
                return "Unknown", get_emoji('neutral'), {}
            
            # Determine current zone
            extreme_discount = pivot_levels['extreme_discount']
            accumulation_upper = pivot_levels.get('accumulation_upper', extreme_discount * 1.2)
            reversal_zone = pivot_levels.get('reversal_zone', accumulation_upper * 1.2)
            strong_support = pivot_levels.get('strong_support', reversal_zone * 1.2)
            
            # Determine zone based on current price
            if current_price <= extreme_discount:
                zone_name = "Extreme Discount"
                zone_emoji = get_emoji('discount')
                is_bullish_zone = True
            elif current_price <= accumulation_upper:
                zone_name = "Accumulation Zone"
                zone_emoji = get_emoji('up')
                is_bullish_zone = True
            elif current_price <= reversal_zone:
                zone_name = "Reversal Zone"
                zone_emoji = get_emoji('neutral')
                is_bullish_zone = False
            elif current_price <= strong_support:
                zone_name = "Strong Support"
                zone_emoji = get_emoji('down')
                is_bullish_zone = False
            else:
                zone_name = "Above Buy Zone"
                zone_emoji = get_emoji('overvalued')
                is_bullish_zone = False
            
            # Prepare zone details
            zone_details = {
                'zone_name': zone_name,
                'zone_emoji': zone_emoji,
                'is_bullish_zone': is_bullish_zone,
                'extreme_discount': extreme_discount,
                'accumulation_lower': pivot_levels.get('accumulation_lower', extreme_discount),
                'accumulation_upper': accumulation_upper,
                'accumulation_mid_range': pivot_levels.get('accumulation_mid_range', 
                    (pivot_levels.get('accumulation_lower', extreme_discount) + accumulation_upper) / 2),
                'reversal_zone': reversal_zone,
                'strong_support': strong_support,
                'recent_low': pivot_levels.get('recent_low', 0),
                'recent_high': pivot_levels.get('recent_high', 0),
                'price_range': pivot_levels.get('price_range', 0)
            }
            
            return zone_name, zone_emoji, zone_details
            
        except Exception as e:
            logger.error(f"Error getting pivot zone: {str(e)}")
            return "Unknown", get_emoji('neutral'), {}
    
    def get_pivot_zone_signal(self, zone_details: Dict[str, Any]) -> Tuple[str, str]:
        """Get pivot zone signal (Bullish/Bearish/Neutral) based on zone"""
        try:
            if not zone_details:
                return "Neutral", get_emoji('neutral')
            
            zone_name = zone_details.get('zone_name', '')
            is_bullish_zone = zone_details.get('is_bullish_zone', False)
            
            if zone_name in ["Extreme Discount", "Accumulation Zone"] and is_bullish_zone:
                return "Bullish", get_emoji('up')
            elif zone_name in ["Above Buy Zone", "Strong Support"] and not is_bullish_zone:
                return "Bearish", get_emoji('down')
            else:
                return "Neutral", get_emoji('neutral')
                
        except Exception as e:
            logger.error(f"Error getting pivot zone signal: {str(e)}")
            return "Neutral", get_emoji('neutral')
    
    def calculate_regression_metrics(self, df: pd.DataFrame, coeffs: np.ndarray) -> Tuple[float, float, float]:
        """Calculate regression quality metrics"""
        try:
            if len(coeffs) == 0:
                return 0.0, 0.0, 0.0
            
            x = np.arange(len(df))
            y = df['close'].values
            
            polynomial = np.poly1d(coeffs)
            y_pred = polynomial(x)
            
            # R-squared
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2) if len(y) > 1 else 1
            r_squared = max(0, min(1, 1 - (ss_res / ss_tot))) if ss_tot != 0 else 0
            
            # Confidence based on R-squared
            confidence = min(100, max(0, r_squared * 100))
            
            # Trend strength based on slope
            if len(coeffs) > 1:
                slope = coeffs[-2]
                trend_strength = min(100, max(0, abs(slope) * 1000))
            else:
                trend_strength = 0
            
            return r_squared, confidence, trend_strength
            
        except Exception as e:
            logger.error(f"Error calculating regression metrics: {str(e)}")
            return 0.0, 0.0, 0.0
    
    def calculate_support_resistance(self, df: pd.DataFrame) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        try:
            if len(df) < 10:
                support = df['low'].min()
                resistance = df['high'].max()
            else:
                # Use recent data
                recent = df.tail(20)
                support = recent['low'].min()
                resistance = recent['high'].max()
            
            # Ensure support < resistance
            if support >= resistance:
                resistance = support * 1.05
            
            return float(support), float(resistance)
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {str(e)}")
            return 0.0, 0.0
    
    def save_daily_forecast_to_db(self, symbol: str, current_price: float, 
                                 forecast_1d: float, forecast_7d: float, 
                                 forecast_14d: float, forecast_30d: float, 
                                 poly_signal: str, poly_emoji: str) -> bool:
        """Save daily polynomial regression forecast to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO hvts_forecast 
                (symbol, current_price, forecast_1d, forecast_7d, forecast_14d, forecast_30d, poly_signal, poly_emoji, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol, current_price, forecast_1d, forecast_7d, 
                forecast_14d, forecast_30d, poly_signal, poly_emoji,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Saved daily forecast for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving daily forecast for {symbol}: {str(e)}")
            return False
    
    def save_fibonacci_data_to_db(self, symbol: str, current_price: float, 
                                 fib_levels: Dict[str, float], fib_1h_signal: str, 
                                 pivot_zone: str) -> bool:
        """Save Fibonacci 1-hour data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO fibonacci_1h 
                (symbol, current_price, fib_level_0, fib_level_23_6, fib_level_38_2, fib_level_50, 
                 fib_level_61_8, fib_level_78_6, fib_level_100, fib_level_127_2, fib_level_161_8,
                 fib_level_261_8, fib_level_423_6, fib_1h_signal, pivot_zone, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol, current_price,
                fib_levels.get('0%', 0), fib_levels.get('23.6%', 0),
                fib_levels.get('38.2%', 0), fib_levels.get('50%', 0),
                fib_levels.get('61.8%', 0), fib_levels.get('78.6%', 0),
                fib_levels.get('100%', 0), fib_levels.get('127.2%', 0),
                fib_levels.get('161.8%', 0), fib_levels.get('261.8%', 0),
                fib_levels.get('423.6%', 0), fib_1h_signal, pivot_zone,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Saved Fibonacci data for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving Fibonacci data for {symbol}: {str(e)}")
            return False
    
    def save_regression_data_to_db(self, symbol: str, current_price: float, 
                                  poly_regression_value: float, poly_signal_daily: str, 
                                  poly_confidence: float, r_squared: float, 
                                  trend_strength: float, support_level: float, 
                                  resistance_level: float, forecast_1d: float, 
                                  forecast_7d: float, forecast_30d: float) -> bool:
        """Save polynomial regression daily data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO polynomial_regression_daily 
                (symbol, current_price, poly_regression_value, poly_signal_daily, poly_confidence,
                 r_squared, trend_strength, support_level, resistance_level,
                 forecast_1d, forecast_7d, forecast_30d, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol, current_price, poly_regression_value, poly_signal_daily,
                poly_confidence, r_squared, trend_strength, support_level,
                resistance_level, forecast_1d, forecast_7d, forecast_30d,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Saved regression data for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving regression data for {symbol}: {str(e)}")
            return False
    
    def save_trading_signal_to_db(self, signal: Dict[str, Any]) -> bool:
        """Save complete trading signal to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO trading_signals 
                (symbol, current_price, poly_1h_signal, fib_15m_signal, fib_signal, 
                 poly_signal, rsi_zone, macd_signal, pivot_zone, overall_signal,
                 forecast_1h, forecast_1d, forecast_7d, forecast_14d, forecast_30d, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal['symbol'], signal['current_price'],
                signal['poly_1h_signal'], signal['fib_15m_signal'],
                signal['fib_signal'], signal['poly_signal'],
                signal['rsi_zone'], signal['macd_signal'],
                signal['pivot_zone'], signal['overall_signal'],
                signal['forecast_1h'], signal['forecast_1d'],
                signal['forecast_7d'], signal['forecast_14d'],
                signal['forecast_30d'], signal['timestamp']
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Saved trading signal for {signal['symbol']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving trading signal for {signal['symbol']}: {str(e)}")
            return False
    
    def update_dashboard_metadata(self, total_symbols: int, update_duration: float, 
                                 status: str = 'success') -> bool:
        """Update dashboard metadata table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO dashboard_metadata 
                (id, last_updated, total_symbols, last_update_status, update_duration_seconds, data_source)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total_symbols,
                status,
                update_duration,
                'gateio'
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Updated dashboard metadata: {total_symbols} symbols, {update_duration:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error updating dashboard metadata: {str(e)}")
            return False
    
    def generate_signal(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Generate trading signal for a symbol with real data only - Updated for precise pivot zones"""
        logger.info(f"{get_emoji('signal')} Generating signal for {symbol}")
        
        try:
            # Fetch real data from Gate.io
            hourly_data = self.fetch_data(symbol, '1h', 100)
            four_hour_data = self.fetch_data(symbol, '4h', 100)
            daily_data = self.fetch_data(symbol, '1d', 100)
            
            # Validate data
            if hourly_data is None or hourly_data.empty:
                logger.error(f"No hourly data for {symbol}")
                return None
            
            if daily_data is None or daily_data.empty:
                logger.error(f"No daily data for {symbol}")
                return None
            
            if four_hour_data is None or four_hour_data.empty:
                logger.warning(f"No 4h data for {symbol}, using hourly data")
                four_hour_data = hourly_data
            
            # Current price from daily data
            current_price = float(daily_data['close'].iloc[-1])
            logger.info(f"{symbol} current price: ${current_price:.4f}")
            
            # 1-hour Polynomial Regression Trend Signal
            poly_1h_signal, poly_1h_emoji, poly_1h_forecast = self.get_poly_signal_1h(hourly_data, current_price)
            
            # 1-hour Fibonacci Analysis
            fib_levels_1h = self.calculate_fibonacci_levels(
                hourly_data['high'].max(), 
                hourly_data['low'].min()
            )
            fib_1h_signal, fib_1h_emoji = self.get_fibonacci_signal(current_price, fib_levels_1h)
            
            # Fibonacci Signal for comparison
            fib_signal, fib_emoji = self.get_fibonacci_signal(current_price, fib_levels_1h)
            
            # Daily Polynomial Regression
            forecast, coeffs = self.polynomial_regression_forecast(daily_data, degree=3, periods=30)
            
            if forecast is not None and coeffs is not None:
                # Extract forecasts
                forecast_1d = forecast[0] if len(forecast) >= 1 else current_price
                forecast_7d = forecast[6] if len(forecast) >= 7 else current_price
                forecast_14d = forecast[13] if len(forecast) >= 14 else current_price
                forecast_30d = forecast[29] if len(forecast) >= 30 else current_price
                
                # Regression metrics
                r_squared, confidence, trend_strength = self.calculate_regression_metrics(daily_data, coeffs)
                
                # Support and resistance
                support, resistance = self.calculate_support_resistance(daily_data)
                
                # Determine trend based on pseudocode logic (1% threshold)
                price_change_1d_pct = ((forecast_1d - current_price) / current_price) * 100
                if price_change_1d_pct > 1.0:  # 1% increase threshold from pseudocode
                    poly_signal, poly_emoji = "Bullish", get_emoji('up')
                elif price_change_1d_pct < -1.0:  # 1% decrease threshold
                    poly_signal, poly_emoji = "Bearish", get_emoji('down')
                else:
                    poly_signal, poly_emoji = "Neutral", get_emoji('neutral')
                
                # Save regression data
                self.save_regression_data_to_db(
                    symbol, current_price,
                    coeffs[-2] if len(coeffs) > 1 else 0,
                    f"{poly_emoji} {poly_signal}",
                    confidence, r_squared, trend_strength,
                    support, resistance,
                    forecast_1d, forecast_7d, forecast_30d
                )
                
                # Save daily forecast
                self.save_daily_forecast_to_db(
                    symbol, current_price, forecast_1d, forecast_7d,
                    forecast_14d, forecast_30d, poly_signal, poly_emoji
                )
            else:
                # Fallback if regression fails
                forecast_1d = forecast_7d = forecast_14d = forecast_30d = current_price
                poly_signal, poly_emoji = "Neutral", get_emoji('neutral')
                r_squared = confidence = trend_strength = 0
                support = resistance = current_price
            
            # RSI Analysis (4-hour) - Updated thresholds from pseudocode
            rsi_values = self.calculate_rsi(four_hour_data['close'])
            current_rsi = rsi_values.iloc[-1] if not rsi_values.empty else 50
            
            # Get RSI zone for display
            rsi_zone, rsi_zone_emoji = self.get_rsi_zone(current_rsi)
            
            # Get RSI signal based on pseudocode thresholds
            if current_rsi < 40:
                rsi_signal, rsi_signal_emoji = "Bullish", get_emoji('up')
            elif current_rsi > 60:
                rsi_signal, rsi_signal_emoji = "Bearish", get_emoji('down')
            else:
                rsi_signal, rsi_signal_emoji = "Neutral", get_emoji('neutral')
            
            # MACD Analysis (4-hour)
            macd_line, signal_line, macd_histogram = self.calculate_macd(four_hour_data['close'])
            macd_signal, macd_emoji = self.get_macd_signal(macd_line, signal_line, macd_histogram)
            
            # NEW: Precise Pivot Zone Analysis
            pivot_levels = self.calculate_pivot_zones(daily_data)
            pivot_zone, pivot_emoji, zone_details = self.get_pivot_zone(current_price, pivot_levels)
            pivot_signal, pivot_signal_emoji = self.get_pivot_zone_signal(zone_details)
            
            # Save Fibonacci data with actual pivot zone
            self.save_fibonacci_data_to_db(
                symbol, current_price, fib_levels_1h,
                f"{fib_1h_emoji} {fib_1h_signal}",
                f"{pivot_emoji} {pivot_zone}"
            )
            
            # Combined signal analysis - Updated for 3+ signal threshold from pseudocode
            # Convert signals to consistent format for counting
            signal_list = [
                ('Poly 1H', poly_1h_signal),
                ('Fibonacci', fib_signal),
                ('Poly Daily', poly_signal),
                ('RSI', rsi_signal),
                ('MACD', macd_signal),
                ('Pivot Zone', pivot_signal)
            ]
            
            # Count bullish and bearish signals
            bull_keywords = ['bull', 'up']
            bear_keywords = ['bear', 'down']
            
            bull_count = 0
            bear_count = 0
            
            for _, signal in signal_list:
                signal_str = str(signal).lower()
                if any(k in signal_str for k in bull_keywords):
                    bull_count += 1
                elif any(k in signal_str for k in bear_keywords):
                    bear_count += 1
            
            # Determine overall signal based on pseudocode logic (3+ signals)
            if bull_count >= 3 and zone_details.get('is_bullish_zone', False):
                overall_signal, overall_emoji = "BUY", get_emoji('up')
            elif bear_count >= 3 and not zone_details.get('is_bullish_zone', False):
                overall_signal, overall_emoji = "SELL", get_emoji('down')
            else:
                overall_signal, overall_emoji = "NEUTRAL", get_emoji('neutral')
            
            # STRONG signals based on additional criteria
            if bull_count >= 4 and pivot_zone in ["Extreme Discount", "Accumulation Zone"]:
                overall_signal, overall_emoji = "STRONG BUY", get_emoji('up')
            elif bear_count >= 4 and pivot_zone in ["Above Buy Zone", "Strong Support"]:
                overall_signal, overall_emoji = "STRONG SELL", get_emoji('down')
            
            # Create signal dictionary with enhanced zone details
            signal_data = {
                'symbol': symbol,
                'current_price': current_price,
                'poly_1h_signal': f"{poly_1h_emoji} {poly_1h_signal}",
                'fib_15m_signal': f"{fib_1h_emoji} {fib_1h_signal}",
                'fib_signal': f"{fib_emoji} {fib_signal}",
                'poly_signal': f"{poly_emoji} {poly_signal}",
                'rsi_zone': f"{rsi_zone_emoji} {rsi_zone} (RSI: {current_rsi:.2f})",
                'rsi_signal': f"{rsi_signal_emoji} {rsi_signal}",
                'macd_signal': f"{macd_emoji} {macd_signal}",
                'pivot_zone': f"{pivot_emoji} {pivot_zone}",
                'pivot_signal': f"{pivot_signal_emoji} {pivot_signal}",
                'overall_signal': f"{overall_emoji} {overall_signal}",
                'overall_signal_type': overall_signal,
                'pivot_zone_type': pivot_zone,
                'pivot_emoji': pivot_emoji,
                'zone_details': zone_details,
                'signal_counts': {'bullish': bull_count, 'bearish': bear_count, 'total': len(signal_list)},
                'forecast_1h': poly_1h_forecast,
                'forecast_1d': forecast_1d,
                'forecast_7d': forecast_7d,
                'forecast_14d': forecast_14d,
                'forecast_30d': forecast_30d,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data_source': 'gateio'
            }
            
            # Save to database
            self.save_trading_signal_to_db(signal_data)
            
            # Enhanced logging for pivot zones
            if zone_details:
                logger.info(f"Pivot Zone Analysis for {symbol}:")
                logger.info(f"  Zone: {pivot_zone} ({pivot_signal})")
                logger.info(f"  Price Range: ${zone_details.get('price_range', 0):.4f}")
                logger.info(f"  Accumulation Zone: ${zone_details.get('accumulation_lower', 0):.4f} - ${zone_details.get('accumulation_upper', 0):.4f}")
                logger.info(f"  Signal Counts: Bullish={bull_count}, Bearish={bear_count}")
            
            logger.info(f"{get_emoji('check')} Generated signal for {symbol}: {overall_signal} ({pivot_zone})")
            return signal_data
            
        except Exception as e:
            logger.error(f"{get_emoji('cross')} Error generating signal for {symbol}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def send_telegram_message(self, message: str) -> bool:
        """Send message to Telegram channel"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.debug("Telegram credentials not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def format_signal_message(self, signal: Dict[str, Any]) -> str:
        """Format signal message for Telegram with enhanced pivot zone info"""
        message = f"""
🚀 <b>{signal['symbol']} Trading Signal</b> 🚀
⏰ {signal['timestamp']}

📊 <b>Current Price:</b> ${signal['current_price']:.4f}

<b>PIVOT ZONE ANALYSIS:</b>
• Zone: {signal['pivot_zone']}
• Signal: {signal['pivot_signal']}

📈 <b>Signals ({signal['signal_counts']['bullish']}/{signal['signal_counts']['total']} bullish):</b>
• 1H Fibonacci: {signal['fib_15m_signal']}
• Machine Learning: {signal['poly_signal']}
• RSI: {signal['rsi_signal']}
• MACD: {signal['macd_signal']}
• Pivot Zone: {signal['pivot_signal']}

🎯 <b>Overall Signal:</b> {signal['overall_signal']}

📅 <b>30-Day Forecast:</b> ${signal['forecast_30d']:.4f}

#{signal['overall_signal_type'].replace(' ', '')} #{signal['symbol'].replace('/', '').replace(':', '').replace('USDT', '')}
#{signal['pivot_zone_type'].replace(' ', '')}Zone
        """
        return message.strip()
    
    def format_summary_message(self, strong_signals: List[Dict[str, Any]]) -> Optional[str]:
        """Format summary message for STRONG BUY/SELL signals"""
        if not strong_signals:
            return None
        
        strong_buy = [s for s in strong_signals if s['overall_signal_type'] == 'STRONG BUY']
        strong_sell = [s for s in strong_signals if s['overall_signal_type'] == 'STRONG SELL']
        
        message = f"""
📊 <b>STRONG SIGNALS SUMMARY</b> 📊
⏰ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

🟢 <b>STRONG BUY ({len(strong_buy)})</b>:
"""
        
        for signal in strong_buy:
            message += f"• {signal['symbol']}: {{ {signal['pivot_emoji']} {signal['pivot_zone_type']} }}\n"
        
        message += f"\n🔴 <b>STRONG SELL ({len(strong_sell)})</b>:"
        
        for signal in strong_sell:
            message += f"• {signal['symbol']}: {{ {signal['pivot_emoji']} {signal['pivot_zone_type']} }}\n"
        
        message += f"\n📈 <b>Total Strong Signals:</b> {len(strong_signals)}/{len(SYMBOLS)}"
        message += f"\n#StrongSignals #TradingAlert"
        
        return message.strip()
    
    def display_console_output(self, signal: Dict[str, Any]):
        """Display formatted output in console with pivot zone details"""
        print("\n" + "="*70)
        print(f"{get_emoji('rocket')} {signal['symbol']} TRADING SIGNAL")
        print(f"{get_emoji('clock')} {signal['timestamp']}")
        print("="*70)
        print(f"{get_emoji('chart')} Current Price: ${signal['current_price']:.4f}")
        
        # Pivot Zone Details
        zone_details = signal.get('zone_details', {})
        if zone_details:
            print(f"\n{get_emoji('portfolio')} PIVOT ZONE ANALYSIS:")
            print(f"   • Zone: {signal['pivot_zone']}")
            print(f"   • Signal: {signal['pivot_signal']}")
            if 'accumulation_lower' in zone_details:
                print(f"   • Accumulation Zone: ${zone_details['accumulation_lower']:.4f} - ${zone_details['accumulation_upper']:.4f}")
            if 'extreme_discount' in zone_details:
                print(f"   • Extreme Discount: <${zone_details['extreme_discount']:.4f}")
        
        print(f"\n{get_emoji('signal')} Signals ({signal.get('signal_counts', {}).get('bullish', 0)}/6 bullish):")
        print(f"   • 1H Fibonacci: {signal['fib_15m_signal']}")
        print(f"   • Machine Learning: {signal['poly_signal']}")
        print(f"   • RSI: {signal['rsi_signal']}")
        print(f"   • MACD: {signal['macd_signal']}")
        print(f"   • Pivot Zone: {signal['pivot_signal']}")
        
        print(f"\n{get_emoji('star')} Overall Signal: {signal['overall_signal']}")
        print(f"\n{get_emoji('clock')} 30-Day Forecast: ${signal['forecast_30d']:.4f}")
        print("="*70)
    
    def run(self, send_telegram: bool = False) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Main execution method - generate signals for all symbols"""
        start_time = time.time()
        logger.info(f"{get_emoji('rocket')} Starting trading signal generation for {len(SYMBOLS)} symbols")
        
        all_signals = []
        strong_signals = []
        successful_symbols = 0
        
        for i, symbol in enumerate(SYMBOLS):
            try:
                logger.info(f"Processing symbol {i+1}/{len(SYMBOLS)}: {symbol}")
                signal = self.generate_signal(symbol)
                
                if signal:
                    all_signals.append(signal)
                    successful_symbols += 1
                    
                    # Display in console
                    self.display_console_output(signal)
                    
                    # Send to Telegram if requested
                    if send_telegram:
                        message = self.format_signal_message(signal)
                        if self.send_telegram_message(message):
                            logger.info(f"{get_emoji('check')} Sent Telegram message for {symbol}")
                        else:
                            logger.warning(f"{get_emoji('warning')} Failed to send Telegram message for {symbol}")
                    
                    # Collect strong signals
                    if signal['overall_signal_type'] in ['STRONG BUY', 'STRONG SELL']:
                        strong_signals.append(signal)
                        logger.info(f"{get_emoji('star')} Found strong signal for {symbol}: {signal['overall_signal_type']}")
                
                else:
                    logger.warning(f"{get_emoji('warning')} Failed to generate signal for {symbol}")
                
                # Rate limiting to avoid API restrictions
                if i < len(SYMBOLS) - 1:
                    wait_time = 3  # 3 seconds between symbols
                    logger.debug(f"Waiting {wait_time} seconds before next symbol...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                logger.error(f"{get_emoji('cross')} Error processing {symbol}: {str(e)}")
                logger.error(traceback.format_exc())
                continue
        
        # Calculate duration and update metadata
        duration = time.time() - start_time
        self.update_dashboard_metadata(
            total_symbols=successful_symbols,
            update_duration=duration,
            status='success' if successful_symbols > 0 else 'failed'
        )
        
        # Send summary to Telegram if requested
        if send_telegram and strong_signals:
            summary_message = self.format_summary_message(strong_signals)
            if summary_message and self.send_telegram_message(summary_message):
                logger.info(f"{get_emoji('check')} Sent Telegram summary with {len(strong_signals)} strong signals")
            else:
                logger.warning(f"{get_emoji('warning')} Failed to send Telegram summary")
        
        # Log completion
        logger.info(f"{get_emoji('check')} Signal generation completed in {duration:.2f} seconds")
        logger.info(f"{get_emoji('check')} Generated signals for {successful_symbols}/{len(SYMBOLS)} symbols")
        logger.info(f"{get_emoji('check')} Found {len(strong_signals)} strong signals")
        
        return all_signals, strong_signals

def run_scheduled_signals():
    """Run trading signals on a schedule (every 1 hour)"""
    logger.info(f"{get_emoji('rocket')} Starting scheduled signal generator")
    
    try:
        generator = TradingSignalGenerator()
    except ValueError as e:
        print(f"\n{get_emoji('cross')} {e}")
        print("Please set GATE_API_KEY and GATE_API_SECRET in your .env file")
        print("Example .env file:")
        print("GATE_API_KEY=your_api_key_here")
        print("GATE_API_SECRET=your_api_secret_here")
        return
    
    print("\n" + "="*70)
    print("TRADING SIGNAL GENERATOR - SCHEDULED MODE")
    print("="*70)
    print(f"{get_emoji('chart')} Symbols: {len(SYMBOLS)}")
    print(f"{get_emoji('clock')} Schedule: Every 1 hour")
    print(f"{get_emoji('database')} Database: {DATABASE_PATH}")
    print("="*70)
    print("Press Ctrl+C to stop the scheduler\n")
    
    iteration = 0
    try:
        while True:
            iteration += 1
            start_time = datetime.now()
            
            print(f"\n{'='*70}")
            print(f"ITERATION #{iteration} - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")
            
            try:
                # Run signal generation
                all_signals, strong_signals = generator.run(send_telegram=True)
                
                if all_signals:
                    print(f"\n{get_emoji('check')} Successfully generated {len(all_signals)} signals")
                    print(f"{get_emoji('star')} Found {len(strong_signals)} strong signals")
                    
                    # Display strong signals
                    if strong_signals:
                        print(f"\n{get_emoji('chart')} STRONG SIGNALS:")
                        for signal in strong_signals:
                            price_change = ((signal['forecast_30d'] - signal['current_price']) / signal['current_price']) * 100
                            print(f"   • {signal['symbol']}: {signal['overall_signal']} | "
                                  f"${signal['current_price']:.4f} → ${signal['forecast_30d']:.4f} ({price_change:+.1f}%) | "
                                  f"Zone: {signal['pivot_zone']}")
                else:
                    print(f"\n{get_emoji('warning')} No signals generated")
                
            except Exception as e:
                print(f"\n{get_emoji('cross')} Error during signal generation: {e}")
                logger.error(f"Error in iteration #{iteration}: {str(e)}")
                logger.error(traceback.format_exc())
            
            # Calculate sleep time (1 hour interval)
            execution_time = (datetime.now() - start_time).total_seconds()
            sleep_time = max(0, 3600 - execution_time)
            
            minutes = int(sleep_time // 60)
            seconds = int(sleep_time % 60)
            
            print(f"\n{get_emoji('clock')} Next update in {minutes} minutes {seconds} seconds")
            print(f"{'='*70}")
            
            # Sleep until next iteration
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print(f"\n\n{get_emoji('info')} Scheduler stopped by user")
        logger.info("Scheduler stopped by user")
    except Exception as e:
        print(f"\n{get_emoji('cross')} Fatal error in scheduler: {e}")
        logger.error(f"Fatal error in scheduler: {str(e)}")

def main():
    """Main function - run once for database update"""
    print("\n" + "="*70)
    print("TRADING SIGNAL GENERATOR - REAL DATA ONLY")
    print("="*70)
    print(f"{get_emoji('chart')} Symbols: {len(SYMBOLS)}")
    print(f"{get_emoji('database')} Database: {DATABASE_PATH}")
    print("="*70)
    
    try:
        generator = TradingSignalGenerator()
    except ValueError as e:
        print(f"\n{get_emoji('cross')} {e}")
        print("\nPlease configure your .env file with Gate.io API keys:")
        print("\n1. Get API keys from Gate.io:")
        print("   - Go to https://www.gate.io/myaccount/apikeys")
        print("   - Create API key with 'Read' permissions")
        print("\n2. Create or edit .env file:")
        print("   GATE_API_KEY=your_api_key_here")
        print("   GATE_API_SECRET=your_api_secret_here")
        print("   TELEGRAM_BOT_TOKEN=optional")
        print("   TELEGRAM_CHAT_ID=optional")
        print("\n3. Run again: python scheduler_v2.py")
        return
    
    print(f"\n{get_emoji('check')} API keys validated successfully")
    print("Generating signals for all symbols...\n")
    
    # Run once
    try:
        all_signals, strong_signals = generator.run(send_telegram=False)
        
        if all_signals:
            print(f"\n{'='*70}")
            print(f"{get_emoji('check')} SIGNAL GENERATION COMPLETE")
            print(f"{'='*70}")
            print(f"{get_emoji('chart')} Total Symbols Processed: {len(all_signals)}/{len(SYMBOLS)}")
            print(f"{get_emoji('star')} Strong Signals Found: {len(strong_signals)}")
            
            # Display strong signals with zone details
            if strong_signals:
                print(f"\n{get_emoji('signal')} STRONG SIGNALS:")
                for signal in strong_signals:
                    price_change = ((signal['forecast_30d'] - signal['current_price']) / signal['current_price']) * 100
                    zone_details = signal.get('zone_details', {})
                    print(f"   • {signal['symbol']}: {signal['overall_signal']} | "
                          f"${signal['current_price']:.4f} → ${signal['forecast_30d']:.4f} ({price_change:+.1f}%) | "
                          f"Zone: {signal['pivot_zone']}")
                    if 'accumulation_lower' in zone_details:
                        print(f"     Accumulation Zone: ${zone_details['accumulation_lower']:.4f} - ${zone_details['accumulation_upper']:.4f}")
            
            # Next steps
            print(f"\n{get_emoji('database')} Database updated: {DATABASE_PATH}")
            print(f"\n{get_emoji('info')} Next steps:")
            print(f"   1. View dashboard: streamlit run app.py")
            print(f"   2. Commit database to GitHub:")
            print(f"      git add trading_signals.db")
            print(f"      git commit -m 'Update trading data'")
            print(f"      git push")
            print(f"   3. Deploy to Streamlit Cloud")
            print(f"   4. Schedule updates (optional):")
            print(f"      python scheduler_v2.py --scheduled")
            
        else:
            print(f"\n{get_emoji('cross')} Failed to generate any signals")
            print("   Check your internet connection and API permissions")
        
        print(f"\n{'='*70}")
        
    except Exception as e:
        print(f"\n{get_emoji('cross')} Error during signal generation: {e}")
        print("Check scheduler.log for details")
        logger.error(f"Error in main execution: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # Check if running in scheduled mode
    if len(sys.argv) > 1 and sys.argv[1] == '--scheduled':
        run_scheduled_signals()
    else:
        main()