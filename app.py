# app.py - COMPLETE TRADING SIGNALS DASHBOARD FOR STREAMLIT CLOUD
import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import time
from typing import List, Dict, Optional
import os
import json
import io

# Page configuration
st.set_page_config(
    page_title="HVTS Trading Signals Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #546E7A;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .signal-card {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .signal-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .bullish {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 5px solid #4CAF50;
    }
    .bearish {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 5px solid #f44336;
    }
    .neutral {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 5px solid #FF9800;
    }
    .extreme-discount {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 5px solid #2196F3;
        border: 2px solid #2196F3;
    }
    .overvalued {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 5px solid #FF9800;
        border: 2px solid #FF9800;
    }
    .portfolio {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 5px solid #4CAF50;
        border: 2px solid #4CAF50;
    }
    .metric-card {
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background: white;
        border: 1px solid #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .fib-level {
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        font-weight: bold;
        display: inline-block;
    }
    .fib-retracement {
        background-color: #E3F2FD;
        color: #1565C0;
        border: 1px solid #90CAF9;
    }
    .fib-extension {
        background-color: #F3E5F5;
        color: #7B1FA2;
        border: 1px solid #CE93D8;
    }
    .regression-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ec 100%);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #5C6BC0;
        border: 1px solid #C5CAE9;
    }
    .info-badge {
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.9rem;
        margin: 5px 0;
        display: inline-block;
        border: 1px solid #90CAF9;
    }
    .discount-badge {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.9rem;
        margin: 5px 0;
        font-weight: bold;
        display: inline-block;
        border: 1px solid #A5D6A7;
    }
    .overvalued-badge {
        background-color: #FFF3E0;
        color: #EF6C00;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.9rem;
        margin: 5px 0;
        font-weight: bold;
        display: inline-block;
        border: 1px solid #FFCC80;
    }
    .portfolio-badge {
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.9rem;
        margin: 5px 0;
        font-weight: bold;
        display: inline-block;
        border: 1px solid #90CAF9;
    }
    .extreme-discount-indicator {
        background: linear-gradient(135deg, #2196F3 0%, #0D47A1 100%);
        color: white;
        padding: 8px 15px;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(33, 150, 243, 0.3);
    }
    .overvalued-indicator {
        background: linear-gradient(135deg, #FF9800 0%, #EF6C00 100%);
        color: white;
        padding: 8px 15px;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(255, 152, 0, 0.3);
    }
    .portfolio-indicator {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 8px 15px;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
    }
    .discount-metric {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(33,150,243,0.2);
        border: 1px solid #90CAF9;
    }
    .overvalued-metric {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(255,152,0,0.2);
        border: 1px solid #FFCC80;
    }
    .portfolio-metric {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(76,175,80,0.2);
        border: 1px solid #A5D6A7;
    }
    .download-btn {
        background: linear-gradient(135deg, #2196F3 0%, #0D47A1 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        text-align: center;
        display: inline-block;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .download-btn:hover {
        background: linear-gradient(135deg, #1976D2 0%, #0D47A1 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
    }
    .data-table {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .status-active {
        background-color: #4CAF50;
    }
    .status-warning {
        background-color: #FF9800;
    }
    .status-error {
        background-color: #F44336;
    }
    .symbol-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    .symbol-badge-bullish {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    .symbol-badge-bearish {
        background-color: #FFEBEE;
        color: #C62828;
    }
    .symbol-badge-neutral {
        background-color: #FFF3E0;
        color: #EF6C00;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.8rem;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
""", unsafe_allow_html=True)

class TradingDashboard:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize dashboard with database connection"""
        # Use absolute path for cloud deployment
        if db_path is None:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(BASE_DIR, "trading_signals.db")
        
        self.db_path = db_path
        self.connection = None
        self.setup_database_connection()
    
    def setup_database_connection(self):
        """Establish database connection - cloud safe"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.row_factory = sqlite3.Row
        except Exception as e:
            st.error(f"❌ Failed to connect to database: {str(e)}")
            # Create an empty connection for demo purposes
            self.connection = sqlite3.connect(':memory:', check_same_thread=False)
    
    def get_database_metadata(self) -> Dict:
        """Get metadata about the database"""
        try:
            # Try to get from dashboard_metadata table first
            try:
                query = """
                    SELECT last_updated, total_symbols, last_update_status 
                    FROM dashboard_metadata 
                    WHERE id = 1
                """
                cursor = self.connection.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                
                if result:
                    return {
                        'last_updated': result[0],
                        'total_symbols': result[1],
                        'status': result[2],
                        'data_source': 'Real Data'
                    }
            except Exception as e:
                pass
            
            # Fallback: get from trading_signals table
            query = "SELECT MAX(timestamp) as last_updated, COUNT(DISTINCT symbol) as total_symbols FROM trading_signals"
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result and result[0] and result[1]:
                return {
                    'last_updated': result[0],
                    'total_symbols': result[1],
                    'status': 'active',
                    'data_source': 'Real Data'
                }
            
            # Check if we have any data at all
            query = "SELECT COUNT(*) as count FROM trading_signals"
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                return {
                    'last_updated': 'Unknown',
                    'total_symbols': result[0],
                    'status': 'active',
                    'data_source': 'Real Data'
                }
            
            return {
                'last_updated': 'No data',
                'total_symbols': 0,
                'status': 'empty',
                'data_source': 'Sample Data'
            }
                
        except Exception as e:
            return {
                'last_updated': 'Error',
                'total_symbols': 0,
                'status': f'error: {str(e)}',
                'data_source': 'Unknown'
            }
    
    def get_all_signals(self) -> pd.DataFrame:
        """Retrieve all trading signals from database"""
        try:
            query = """
                SELECT 
                    symbol,
                    current_price,
                    poly_1h_signal,
                    fib_15m_signal,
                    fib_signal,
                    poly_signal,
                    rsi_zone,
                    macd_signal,
                    pivot_zone,
                    overall_signal,
                    forecast_1h,
                    forecast_1d,
                    forecast_7d,
                    forecast_14d,
                    forecast_30d,
                    timestamp,
                    created_at
                FROM trading_signals
                ORDER BY timestamp DESC
            """
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            st.error(f"Error fetching signals: {str(e)}")
            return pd.DataFrame()
    
    def get_hvts_forecast(self) -> pd.DataFrame:
        """Retrieve HVTS forecast data"""
        try:
            query = """
                SELECT 
                    symbol,
                    current_price,
                    forecast_1d,
                    forecast_7d,
                    forecast_14d,
                    forecast_30d,
                    poly_signal,
                    poly_emoji,
                    timestamp
                FROM hvts_forecast
                ORDER BY timestamp DESC
            """
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def get_fibonacci_data(self) -> pd.DataFrame:
        """Retrieve Fibonacci 1-hour indicator data - LATEST PER SYMBOL"""
        try:
            # First check if table exists
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fibonacci_1h'")
            if not cursor.fetchone():
                return pd.DataFrame()
            
            # Try the complex query first
            query = """
                SELECT 
                    f1.*
                FROM fibonacci_1h f1
                INNER JOIN (
                    SELECT symbol, MAX(timestamp) as max_timestamp
                    FROM fibonacci_1h
                    GROUP BY symbol
                ) f2 ON f1.symbol = f2.symbol AND f1.timestamp = f2.max_timestamp
                ORDER BY f1.symbol
            """
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            # Fallback to simple query
            try:
                query = """
                    SELECT 
                        symbol,
                        current_price,
                        fib_level_0,
                        fib_level_23_6,
                        fib_level_38_2,
                        fib_level_50,
                        fib_level_61_8,
                        fib_level_78_6,
                        fib_level_100,
                        fib_level_127_2,
                        fib_level_161_8,
                        fib_level_261_8,
                        fib_level_423_6,
                        fib_1h_signal,
                        pivot_zone,
                        timestamp
                    FROM fibonacci_1h
                    ORDER BY timestamp DESC
                """
                df = pd.read_sql_query(query, self.connection)
                # Deduplicate in Python
                df = df.sort_values(['symbol', 'timestamp'], ascending=[True, False])
                df = df.drop_duplicates(subset=['symbol'], keep='first')
                return df
            except Exception as e2:
                return pd.DataFrame()
    
    def get_regression_data(self) -> pd.DataFrame:
        """Retrieve Polynomial Regression Daily indicator data - LATEST PER SYMBOL"""
        try:
            # First check if table exists
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='polynomial_regression_daily'")
            if not cursor.fetchone():
                return pd.DataFrame()
            
            # Try the complex query first
            query = """
                SELECT 
                    r1.*
                FROM polynomial_regression_daily r1
                INNER JOIN (
                    SELECT symbol, MAX(timestamp) as max_timestamp
                    FROM polynomial_regression_daily
                    GROUP BY symbol
                ) r2 ON r1.symbol = r2.symbol AND r1.timestamp = r2.max_timestamp
                ORDER BY r1.symbol
            """
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            # Fallback to simple query
            try:
                query = """
                    SELECT 
                        symbol,
                        current_price,
                        poly_regression_value,
                        poly_signal_daily,
                        poly_confidence,
                        r_squared,
                        trend_strength,
                        support_level,
                        resistance_level,
                        forecast_1d,
                        forecast_7d,
                        forecast_30d,
                        timestamp
                    FROM polynomial_regression_daily
                    ORDER BY timestamp DESC
                """
                df = pd.read_sql_query(query, self.connection)
                # Deduplicate in Python
                df = df.sort_values(['symbol', 'timestamp'], ascending=[True, False])
                df = df.drop_duplicates(subset=['symbol'], keep='first')
                return df
            except Exception as e2:
                return pd.DataFrame()
    
    def get_extreme_discount_signals(self) -> pd.DataFrame:
        """Retrieve signals where price is in Extreme Discount Zone"""
        try:
            query = """
                SELECT 
                    symbol,
                    current_price,
                    poly_1h_signal,
                    fib_15m_signal,
                    fib_signal,
                    poly_signal,
                    rsi_zone,
                    macd_signal,
                    pivot_zone,
                    overall_signal,
                    forecast_1h,
                    forecast_1d,
                    forecast_7d,
                    forecast_14d,
                    forecast_30d,
                    timestamp
                FROM trading_signals
                WHERE pivot_zone LIKE '%EXTREME DISCOUNT%' 
                   OR pivot_zone LIKE '%Extreme Discount%'
                   OR pivot_zone LIKE '%extreme discount%'
                ORDER BY timestamp DESC
            """
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def get_overvalued_signals(self) -> pd.DataFrame:
        """Retrieve signals where price is in ABOVE BUY ZONE"""
        try:
            query = """
                SELECT 
                    symbol,
                    current_price,
                    poly_1h_signal,
                    fib_15m_signal,
                    fib_signal,
                    poly_signal,
                    rsi_zone,
                    macd_signal,
                    pivot_zone,
                    overall_signal,
                    forecast_1h,
                    forecast_1d,
                    forecast_7d,
                    forecast_14d,
                    forecast_30d,
                    timestamp
                FROM trading_signals
                WHERE pivot_zone LIKE '%ABOVE BUY ZONE%' 
                   OR pivot_zone LIKE '%Above Buy Zone%'
                   OR pivot_zone LIKE '%above buy zone%'
                ORDER BY timestamp DESC
            """
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def get_portfolio_signals(self) -> pd.DataFrame:
        """Get portfolio signals - Bullish Regression + Extreme Discount"""
        try:
            # Get all signals and deduplicate
            all_signals = self.get_all_signals()
            if all_signals.empty:
                return pd.DataFrame()
            
            all_signals = all_signals.sort_values(['symbol', 'timestamp'], ascending=[True, False])
            all_signals = all_signals.drop_duplicates(subset=['symbol'], keep='first')
            
            # Get regression data
            reg_df = self.get_regression_data()
            
            # Get extreme discount signals
            discount_df = self.get_extreme_discount_signals()
            
            if reg_df.empty or discount_df.empty:
                return pd.DataFrame()
            
            # Filter for bullish regression signals
            bullish_regression = reg_df[
                reg_df['poly_signal_daily'].str.contains('BULLISH', case=False, na=False)
            ]
            
            if bullish_regression.empty:
                return pd.DataFrame()
            
            # Get symbols that are both bullish regression AND extreme discount
            portfolio_symbols = set(bullish_regression['symbol']).intersection(set(discount_df['symbol']))
            
            if not portfolio_symbols:
                return pd.DataFrame()
            
            # Get full data for these symbols
            portfolio_df = all_signals[all_signals['symbol'].isin(portfolio_symbols)]
            
            return portfolio_df
            
        except Exception as e:
            return pd.DataFrame()
    
    def get_signal_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate statistics from signals"""
        if df.empty:
            return {}
        
        stats = {
            'total_symbols': len(df),
            'strong_buy': len(df[df['overall_signal'].str.contains('STRONG BUY', case=False, na=False)]),
            'buy': len(df[df['overall_signal'].str.contains('BUY', case=False, na=False) & ~df['overall_signal'].str.contains('STRONG', case=False, na=False)]),
            'strong_sell': len(df[df['overall_signal'].str.contains('STRONG SELL', case=False, na=False)]),
            'sell': len(df[df['overall_signal'].str.contains('SELL', case=False, na=False) & ~df['overall_signal'].str.contains('STRONG', case=False, na=False)]),
            'neutral': len(df[df['overall_signal'].str.contains('NEUTRAL', case=False, na=False)]),
            'latest_update': df['timestamp'].max() if len(df) > 0 else 'N/A'
        }
        
        # Calculate average price change forecasts
        if 'forecast_30d' in df.columns and 'current_price' in df.columns:
            df_temp = df.dropna(subset=['forecast_30d', 'current_price']).copy()
            if not df_temp.empty:
                df_temp['price_change_pct'] = ((df_temp['forecast_30d'] - df_temp['current_price']) / df_temp['current_price']) * 100
                stats['avg_price_change_30d'] = df_temp['price_change_pct'].mean()
                
                if not df_temp['price_change_pct'].empty:
                    try:
                        max_idx = df_temp['price_change_pct'].idxmax()
                        min_idx = df_temp['price_change_pct'].idxmin()
                        stats['max_bullish'] = df_temp.loc[max_idx, 'symbol'] if max_idx in df_temp.index else 'N/A'
                        stats['max_bearish'] = df_temp.loc[min_idx, 'symbol'] if min_idx in df_temp.index else 'N/A'
                        stats['max_bullish_change'] = df_temp.loc[max_idx, 'price_change_pct'] if max_idx in df_temp.index else 0
                        stats['max_bearish_change'] = df_temp.loc[min_idx, 'price_change_pct'] if min_idx in df_temp.index else 0
                    except:
                        stats['max_bullish'] = 'N/A'
                        stats['max_bearish'] = 'N/A'
                        stats['max_bullish_change'] = 0
                        stats['max_bearish_change'] = 0
        
        return stats
    
    def get_extreme_discount_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate statistics for extreme discount signals"""
        if df.empty:
            return {}
        
        stats = {
            'total_symbols': len(df),
            'strong_buy': len(df[df['overall_signal'].str.contains('STRONG BUY', case=False, na=False)]),
            'buy': len(df[df['overall_signal'].str.contains('BUY', case=False, na=False) & ~df['overall_signal'].str.contains('STRONG', case=False, na=False)]),
            'strong_sell': len(df[df['overall_signal'].str.contains('STRONG SELL', case=False, na=False)]),
            'sell': len(df[df['overall_signal'].str.contains('SELL', case=False, na=False) & ~df['overall_signal'].str.contains('STRONG', case=False, na=False)]),
            'neutral': len(df[df['overall_signal'].str.contains('NEUTRAL', case=False, na=False)]),
            'avg_current_price': df['current_price'].mean() if len(df) > 0 else 0,
            'avg_forecast_30d_change': 0,
            'top_potential_gainers': []
        }
        
        if 'forecast_30d' in df.columns and 'current_price' in df.columns:
            df_temp = df.dropna(subset=['forecast_30d', 'current_price']).copy()
            if not df_temp.empty:
                df_temp['forecast_change_30d'] = ((df_temp['forecast_30d'] - df_temp['current_price']) / df_temp['current_price']) * 100
                stats['avg_forecast_30d_change'] = df_temp['forecast_change_30d'].mean()
                
                top_gainers = df_temp.nlargest(5, 'forecast_change_30d')
                stats['top_potential_gainers'] = top_gainers[['symbol', 'current_price', 'forecast_30d', 'forecast_change_30d']].to_dict('records')
        
        return stats
    
    def get_overvalued_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate statistics for overvalued signals"""
        if df.empty:
            return {}
        
        stats = {
            'total_symbols': len(df),
            'strong_buy': len(df[df['overall_signal'].str.contains('STRONG BUY', case=False, na=False)]),
            'buy': len(df[df['overall_signal'].str.contains('BUY', case=False, na=False) & ~df['overall_signal'].str.contains('STRONG', case=False, na=False)]),
            'strong_sell': len(df[df['overall_signal'].str.contains('STRONG SELL', case=False, na=False)]),
            'sell': len(df[df['overall_signal'].str.contains('SELL', case=False, na=False) & ~df['overall_signal'].str.contains('STRONG', case=False, na=False)]),
            'neutral': len(df[df['overall_signal'].str.contains('NEUTRAL', case=False, na=False)]),
            'avg_current_price': df['current_price'].mean() if len(df) > 0 else 0,
            'avg_forecast_30d_change': 0,
            'top_potential_decliners': []
        }
        
        if 'forecast_30d' in df.columns and 'current_price' in df.columns:
            df_temp = df.dropna(subset=['forecast_30d', 'current_price']).copy()
            if not df_temp.empty:
                df_temp['forecast_change_30d'] = ((df_temp['forecast_30d'] - df_temp['current_price']) / df_temp['current_price']) * 100
                stats['avg_forecast_30d_change'] = df_temp['forecast_change_30d'].mean()
                
                top_decliners = df_temp.nsmallest(5, 'forecast_change_30d')
                stats['top_potential_decliners'] = top_decliners[['symbol', 'current_price', 'forecast_30d', 'forecast_change_30d']].to_dict('records')
        
        return stats
    
    def get_portfolio_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate statistics for portfolio signals"""
        if df.empty:
            return {}
        
        stats = {
            'total_symbols': len(df),
            'symbols_list': df['symbol'].tolist(),
            'avg_current_price': df['current_price'].mean() if len(df) > 0 else 0,
            'avg_forecast_30d_change': 0,
            'top_potential_gainers': []
        }
        
        if 'forecast_30d' in df.columns and 'current_price' in df.columns:
            df_temp = df.dropna(subset=['forecast_30d', 'current_price']).copy()
            if not df_temp.empty:
                df_temp['forecast_change_30d'] = ((df_temp['forecast_30d'] - df_temp['current_price']) / df_temp['current_price']) * 100
                stats['avg_forecast_30d_change'] = df_temp['forecast_change_30d'].mean()
                
                top_gainers = df_temp.nlargest(5, 'forecast_change_30d')
                stats['top_potential_gainers'] = top_gainers[['symbol', 'current_price', 'forecast_30d', 'forecast_change_30d']].to_dict('records')
        
        return stats
    
    def extract_signal_type(self, signal_str: str) -> str:
        """Extract signal type from formatted string"""
        if isinstance(signal_str, str):
            signal_upper = signal_str.upper()
            if 'STRONG BUY' in signal_upper:
                return 'STRONG BUY'
            elif 'BUY' in signal_upper and 'STRONG' not in signal_upper:
                return 'BUY'
            elif 'STRONG SELL' in signal_upper:
                return 'STRONG SELL'
            elif 'SELL' in signal_upper and 'STRONG' not in signal_upper:
                return 'SELL'
            elif 'NEUTRAL' in signal_upper:
                return 'NEUTRAL'
        return 'UNKNOWN'
    
    def create_price_forecast_chart(self, symbol: str, current_price: float, 
                                   forecast_1h: float, forecast_1d: float, 
                                   forecast_7d: float, forecast_14d: float, 
                                   forecast_30d: float) -> go.Figure:
        """Create price forecast chart for a symbol"""
        try:
            time_periods = ['Current', '1H', '1D', '7D', '14D', '30D']
            prices = [current_price, forecast_1h, forecast_1d, forecast_7d, forecast_14d, forecast_30d]
            
            # Ensure all prices are valid numbers
            prices = [float(p) if pd.notna(p) and p is not None else current_price for p in prices]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=time_periods,
                y=prices,
                mode='lines+markers',
                name='Price Forecast',
                line=dict(color='#1E88E5', width=3),
                marker=dict(size=8, color='#1E88E5')
            ))
            
            # Add percentage change annotations
            for i, price in enumerate(prices[1:], 1):
                pct_change = ((price - current_price) / current_price) * 100
                if abs(pct_change) > 0.1:  # Only show significant changes
                    fig.add_annotation(
                        x=time_periods[i],
                        y=price,
                        text=f"{pct_change:+.1f}%",
                        showarrow=True,
                        arrowhead=1,
                        ax=0,
                        ay=-40 if pct_change >= 0 else 40,
                        font=dict(color='green' if pct_change >= 0 else 'red', size=10)
                    )
            
            fig.update_layout(
                title=f'{symbol} Price Forecast',
                xaxis_title='Time Period',
                yaxis_title='Price (USDT)',
                template='plotly_white',
                hovermode='x unified',
                height=400,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            return fig
        except Exception as e:
            # Return empty figure on error
            fig = go.Figure()
            fig.update_layout(
                title=f'{symbol} Price Forecast',
                xaxis_title='Time Period',
                yaxis_title='Price (USDT)',
                template='plotly_white',
                height=400
            )
            return fig
    
    def create_fibonacci_chart(self, symbol: str, current_price: float, fib_levels: dict) -> go.Figure:
        """Create Fibonacci retracement/extension chart"""
        try:
            fig = go.Figure()
            
            fib_labels = {
                '0': '0.0%',
                '23_6': '23.6%',
                '38_2': '38.2%',
                '50': '50.0%',
                '61_8': '61.8%',
                '78_6': '78.6%',
                '100': '100.0%',
                '127_2': '127.2%',
                '161_8': '161.8%',
                '261_8': '261.8%',
                '423_6': '423.6%'
            }
            
            levels = []
            labels = []
            colors = []
            
            for key, label in fib_labels.items():
                level_key = f'fib_level_{key}'
                if level_key in fib_levels and fib_levels[level_key] is not None:
                    try:
                        level_value = float(fib_levels[level_key])
                        levels.append(level_value)
                        labels.append(label)
                        
                        if key in ['0', '100']:
                            colors.append('#FF6B6B')
                        elif key in ['23_6', '38_2', '50', '61_8', '78_6']:
                            colors.append('#4ECDC4')
                        else:
                            colors.append('#FFD166')
                    except:
                        continue
            
            if not levels:
                # Return empty figure if no valid levels
                fig.update_layout(
                    title=f'{symbol} - Fibonacci 1h Levels',
                    xaxis_title='Time',
                    yaxis_title='Price (USDT)',
                    template='plotly_white',
                    height=500
                )
                return fig
            
            for level, label, color in zip(levels, labels, colors):
                fig.add_hline(
                    y=level,
                    line_dash="dash",
                    line_color=color,
                    annotation_text=label,
                    annotation_position="right",
                    annotation_font_size=10,
                    annotation_font_color=color
                )
            
            fig.add_hline(
                y=current_price,
                line_dash="solid",
                line_color="#1E88E5",
                line_width=3,
                annotation_text=f"Current: ${current_price:.4f}",
                annotation_position="left",
                annotation_font_size=12,
                annotation_font_color="#1E88E5"
            )
            
            # Find price position between levels
            price_position = None
            sorted_levels = sorted(zip(levels, labels), key=lambda x: x[0], reverse=True)
            
            for i in range(len(sorted_levels) - 1):
                upper_level, upper_label = sorted_levels[i]
                lower_level, lower_label = sorted_levels[i + 1]
                
                if upper_level >= current_price >= lower_level:
                    price_position = f"Between {upper_label} and {lower_label}"
                    break
            
            if price_position:
                fig.add_annotation(
                    x=0.5,
                    y=0.95,
                    xref="paper",
                    yref="paper",
                    text=f"Price Position: {price_position}",
                    showarrow=False,
                    font=dict(size=12, color="#333"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#333",
                    borderwidth=1,
                    borderpad=4
                )
            
            fig.update_layout(
                title=f'{symbol} - Fibonacci 1h Levels',
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis_title='Price (USDT)',
                template='plotly_white',
                height=500,
                showlegend=False,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            return fig
        except Exception as e:
            # Return empty figure on error
            fig = go.Figure()
            fig.update_layout(
                title=f'{symbol} - Fibonacci 1h Levels',
                xaxis_title='Time',
                yaxis_title='Price (USDT)',
                template='plotly_white',
                height=500
            )
            return fig
    
    def create_regression_chart(self, symbol: str, current_price: float, 
                               regression_value: float, support: float, 
                               resistance: float, forecast_1d: float, 
                               forecast_7d: float, forecast_30d: float) -> go.Figure:
        """Create Polynomial Regression chart"""
        try:
            x_points = np.array([-2, -1, 0, 1, 2, 3, 4])
            y_points = current_price + regression_value * x_points
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=x_points,
                y=y_points,
                mode='lines',
                name='Regression Line',
                line=dict(color='#5C6BC0', width=3, dash='solid')
            ))
            
            fig.add_trace(go.Scatter(
                x=[0],
                y=[current_price],
                mode='markers+text',
                name='Current Price',
                marker=dict(size=15, color='#1E88E5'),
                text=[f'Current: ${current_price:.4f}'],
                textposition="top center"
            ))
            
            forecast_points = [
                (1, forecast_1d, '1D Forecast'),
                (2, forecast_7d, '7D Forecast'),
                (4, forecast_30d, '30D Forecast')
            ]
            
            for x, y, label in forecast_points:
                if pd.notna(y) and y > 0:
                    fig.add_trace(go.Scatter(
                        x=[x],
                        y=[y],
                        mode='markers+text',
                        name=label,
                        marker=dict(size=12, color='#4CAF50'),
                        text=[f'{label}: ${y:.4f}'],
                        textposition="top center"
                    ))
            
            if pd.notna(support) and support > 0:
                fig.add_hline(
                    y=support,
                    line_dash="dash",
                    line_color="#FF9800",
                    annotation_text=f"Support: ${support:.4f}",
                    annotation_position="right"
                )
            
            if pd.notna(resistance) and resistance > 0:
                fig.add_hline(
                    y=resistance,
                    line_dash="dash",
                    line_color="#F44336",
                    annotation_text=f"Resistance: ${resistance:.4f}",
                    annotation_position="right"
                )
            
            if len(y_points) > 1:
                try:
                    trend_angle = np.arctan((y_points[-1] - y_points[0]) / (x_points[-1] - x_points[0])) * 180 / np.pi
                    trend_strength = min(100, max(0, abs(trend_angle) / 45 * 100))
                    
                    fig.add_annotation(
                        x=0.5,
                        y=0.1,
                        xref="paper",
                        yref="paper",
                        text=f"Trend Strength: {trend_strength:.1f}%",
                        showarrow=False,
                        font=dict(size=12, color="#333"),
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#333",
                        borderwidth=1,
                        borderpad=4
                    )
                except:
                    pass
            
            fig.update_layout(
                title=f'{symbol} - Polynomial Regression Daily',
                xaxis_title='Time (Relative)',
                yaxis_title='Price (USDT)',
                template='plotly_white',
                height=500,
                showlegend=True,
                hovermode='x unified',
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            return fig
        except Exception as e:
            # Return empty figure on error
            fig = go.Figure()
            fig.update_layout(
                title=f'{symbol} - Polynomial Regression Daily',
                xaxis_title='Time (Relative)',
                yaxis_title='Price (USDT)',
                template='plotly_white',
                height=500
            )
            return fig
    
    def create_extreme_discount_chart(self, discount_df: pd.DataFrame) -> go.Figure:
        """Create chart showing extreme discount symbols with their forecast gains"""
        if discount_df.empty:
            return go.Figure()
        
        try:
            df_temp = discount_df.copy()
            df_temp = df_temp.dropna(subset=['forecast_30d', 'current_price'])
            if df_temp.empty:
                return go.Figure()
            
            df_temp['potential_gain'] = ((df_temp['forecast_30d'] - df_temp['current_price']) / df_temp['current_price']) * 100
            df_temp = df_temp.sort_values('potential_gain', ascending=False)
            
            display_df = df_temp.head(15)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=display_df['symbol'],
                y=display_df['potential_gain'],
                name='30D Potential Gain %',
                marker_color='#2196F3',
                text=[f"{x:.1f}%" for x in display_df['potential_gain']],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Current: $%{customdata[0]:.4f}<br>Forecast: $%{customdata[1]:.4f}<br>Gain: %{y:.1f}%<extra></extra>',
                customdata=display_df[['current_price', 'forecast_30d']].values
            ))
            
            avg_gain = display_df['potential_gain'].mean()
            if not pd.isna(avg_gain):
                fig.add_hline(
                    y=avg_gain,
                    line_dash="dash",
                    line_color="#FF9800",
                    annotation_text=f"Avg: {avg_gain:.1f}%",
                    annotation_position="right"
                )
            
            fig.update_layout(
                title='Extreme Discount Zone - Top 15 by 30D Potential Gain',
                xaxis_title='Symbol',
                yaxis_title='30D Potential Gain (%)',
                template='plotly_white',
                height=500,
                showlegend=False,
                hovermode='x unified',
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            return fig
        except Exception as e:
            return go.Figure()
    
    def create_overvalued_chart(self, overvalued_df: pd.DataFrame) -> go.Figure:
        """Create chart showing overvalued symbols with their forecast declines"""
        if overvalued_df.empty:
            return go.Figure()
        
        try:
            df_temp = overvalued_df.copy()
            df_temp = df_temp.dropna(subset=['forecast_30d', 'current_price'])
            if df_temp.empty:
                return go.Figure()
            
            df_temp['potential_change'] = ((df_temp['forecast_30d'] - df_temp['current_price']) / df_temp['current_price']) * 100
            df_temp = df_temp.sort_values('potential_change', ascending=True)
            
            display_df = df_temp.head(15)
            
            fig = go.Figure()
            
            colors = ['#FF9800' if x >= 0 else '#F44336' for x in display_df['potential_change']]
            
            fig.add_trace(go.Bar(
                x=display_df['symbol'],
                y=display_df['potential_change'],
                name='30D Potential Change %',
                marker_color=colors,
                text=[f"{x:+.1f}%" for x in display_df['potential_change']],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Current: $%{customdata[0]:.4f}<br>Forecast: $%{customdata[1]:.4f}<br>Change: %{y:+.1f}%<extra></extra>',
                customdata=display_df[['current_price', 'forecast_30d']].values
            ))
            
            avg_change = display_df['potential_change'].mean()
            if not pd.isna(avg_change):
                fig.add_hline(
                    y=avg_change,
                    line_dash="dash",
                    line_color="#FF5722",
                    annotation_text=f"Avg: {avg_change:+.1f}%",
                    annotation_position="right"
                )
            
            fig.update_layout(
                title='Overvalued (Above Buy Zone) - Top 15 by 30D Potential Change',
                xaxis_title='Symbol',
                yaxis_title='30D Potential Change (%)',
                template='plotly_white',
                height=500,
                showlegend=False,
                hovermode='x unified',
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            return fig
        except Exception as e:
            return go.Figure()
    
    def create_signal_distribution_chart(self, signals_df: pd.DataFrame) -> go.Figure:
        """Create chart showing signal distribution"""
        if signals_df.empty:
            return go.Figure()
        
        try:
            signals_df['signal_type'] = signals_df['overall_signal'].apply(self.extract_signal_type)
            signal_counts = signals_df['signal_type'].value_counts()
            
            color_map = {
                'STRONG BUY': '#4CAF50',
                'BUY': '#8BC34A',
                'NEUTRAL': '#FF9800',
                'SELL': '#F44336',
                'STRONG SELL': '#D32F2F',
                'UNKNOWN': '#9E9E9E'
            }
            
            colors = [color_map.get(sig, '#9E9E9E') for sig in signal_counts.index]
            
            fig = go.Figure(data=[go.Pie(
                labels=signal_counts.index,
                values=signal_counts.values,
                hole=.3,
                marker=dict(colors=colors),
                textinfo='label+percent',
                hoverinfo='label+value+percent',
                textposition='inside'
            )])
            
            fig.update_layout(
                title='Signal Distribution',
                template='plotly_white',
                height=400,
                showlegend=True,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            return fig
        except Exception as e:
            return go.Figure()
    
    def filter_signals(self, df: pd.DataFrame, filter_type: str = 'all') -> pd.DataFrame:
        """Filter signals based on type"""
        if df.empty:
            return df
        
        df_lower = df.copy()
        df_lower['overall_signal_lower'] = df_lower['overall_signal'].str.lower()
        
        if filter_type == 'strong_buy':
            return df[df_lower['overall_signal_lower'].str.contains('strong buy', na=False)]
        elif filter_type == 'buy':
            return df[df_lower['overall_signal_lower'].str.contains('buy', na=False) & 
                     ~df_lower['overall_signal_lower'].str.contains('strong', na=False)]
        elif filter_type == 'strong_sell':
            return df[df_lower['overall_signal_lower'].str.contains('strong sell', na=False)]
        elif filter_type == 'sell':
            return df[df_lower['overall_signal_lower'].str.contains('sell', na=False) & 
                     ~df_lower['overall_signal_lower'].str.contains('strong', na=False)]
        elif filter_type == 'neutral':
            return df[df_lower['overall_signal_lower'].str.contains('neutral', na=False)]
        else:
            return df
    
    def get_portfolio_symbols_csv(self, portfolio_df: pd.DataFrame) -> str:
        """Generate CSV content for portfolio symbols in the requested format"""
        if portfolio_df.empty:
            return ""
        
        symbols = [f"'{symbol}/USDT'" for symbol in portfolio_df['symbol'].tolist()]
        csv_content = ",".join(symbols)
        
        return csv_content
    
    def save_portfolio_csv(self, portfolio_df: pd.DataFrame) -> tuple:
        """Save portfolio symbols to CSV file and return filename and content"""
        if portfolio_df.empty:
            return "", ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_{timestamp}.csv"
        
        symbols = [f"'{symbol}/USDT'" for symbol in portfolio_df['symbol'].tolist()]
        csv_content = ",".join(symbols)
        
        return filename, csv_content

def main():
    """Main Streamlit application"""
    # Check if database exists
    db_exists = os.path.exists("trading_signals.db")
    
    # Initialize dashboard
    dashboard = TradingDashboard()
    
    # Get database metadata
    metadata = dashboard.get_database_metadata()
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 class='main-header'>📈 HVTS Trading Signals Dashboard</h1>", unsafe_allow_html=True)
        
        # Show database info
        status_color = "#4CAF50" if metadata.get('total_symbols', 0) > 0 else "#FF9800"
        status_text = "🟢 Active" if metadata.get('total_symbols', 0) > 0 else "🟡 No Data"
        
        st.markdown(f"""
        <div style='text-align: center; color: #546E7A; margin-bottom: 20px; padding: 10px; border-radius: 10px; background-color: {status_color}20; border: 1px solid {status_color}50;'>
            <strong>📊 Database:</strong> {metadata.get('total_symbols', 0)} symbols | 
            <strong>⏰ Last Updated:</strong> {metadata.get('last_updated', 'Never')} | 
            <strong>📁 Source:</strong> {metadata.get('data_source', 'Unknown')}
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 Dashboard Controls")
        
        # Manual refresh only (auto-refresh disabled for Streamlit Cloud)
        if st.button("🔄 Refresh Dashboard", use_container_width=True, type="primary"):
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Signal Filters")
        
        signal_filter = st.selectbox(
            "Filter by Signal Type",
            ["All Signals", "STRONG BUY", "BUY", "NEUTRAL", "SELL", "STRONG SELL"]
        )
        
        st.markdown("---")
        st.markdown("### 📈 Display Options")
        show_forecasts = st.checkbox("Show Price Forecast Charts", value=True)
        show_charts = st.checkbox("Show Analysis Charts", value=True)
        show_detailed = st.checkbox("Show Detailed Views", value=True)
        
        st.markdown("---")
        st.markdown("### 📦 Database Info")
        
        if not db_exists:
            st.error("⚠️ Database not found")
            st.info("Run `python update_db.py` locally to generate real data.")
        else:
            if metadata.get('total_symbols', 0) == 0:
                st.warning("⚠️ Database is empty")
            else:
                st.success(f"✅ {metadata.get('total_symbols', 0)} symbols loaded")
            
            st.info(f"**Last Updated:** {metadata.get('last_updated', 'Unknown')}")
            st.info(f"**Data Source:** {metadata.get('data_source', 'Unknown')}")
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        **HVTS Trading Signals Dashboard**
        
        This dashboard displays trading signals 
        generated by algorithmic analysis of 
        cryptocurrency markets.
        
        • Data from Gate.io Exchange
        • Updated hourly
        • 9 different analysis views
        """)
    
    # Main tabs - ALL 9 TABS
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📊 Overview", "📈 All Signals", "🎯 Strong Signals", 
        "📅 Forecasts", "📐 Fibonacci", "📈 Regression", 
        "🔥 Extreme Discount", "💰 Portfolio", "⚠️ Overvalued"
    ])
    
    # Load data once for all tabs
    with st.spinner("📊 Loading trading signals..."):
        signals_df = dashboard.get_all_signals()
        hvts_df = dashboard.get_hvts_forecast()
        fib_df = dashboard.get_fibonacci_data()
        reg_df = dashboard.get_regression_data()
        extreme_discount_df = dashboard.get_extreme_discount_signals()
        overvalued_df = dashboard.get_overvalued_signals()
        portfolio_df = dashboard.get_portfolio_signals()
        
        # Get stats
        if signals_df.empty:
            stats = {}
            discount_stats = {}
            overvalued_stats = {}
            portfolio_stats = {}
            
            if not db_exists:
                st.error("❌ Database file not found. Run `python update_db.py` locally to generate data.")
            else:
                st.warning("⚠️ No signals found in database. The database may be empty.")
        else:
            stats = dashboard.get_signal_stats(signals_df)
            discount_stats = dashboard.get_extreme_discount_stats(extreme_discount_df)
            overvalued_stats = dashboard.get_overvalued_stats(overvalued_df)
            portfolio_stats = dashboard.get_portfolio_stats(portfolio_df)
    
    # TAB 1: OVERVIEW
    with tab1:
        st.markdown("<h2 class='sub-header'>📊 Market Overview</h2>", unsafe_allow_html=True)
        
        if stats and stats.get('total_symbols', 0) > 0:
            # Metrics row
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.metric("Total Symbols", stats.get('total_symbols', 0))
            with col2:
                strong_buy = stats.get('strong_buy', 0)
                st.metric("STRONG BUY", strong_buy, 
                         delta=f"+{strong_buy}" if strong_buy > 0 else None)
            with col3:
                buy = stats.get('buy', 0)
                st.metric("BUY", buy, 
                         delta=f"+{buy}" if buy > 0 else None)
            with col4:
                strong_sell = stats.get('strong_sell', 0)
                st.metric("STRONG SELL", strong_sell, 
                         delta=f"-{strong_sell}" if strong_sell > 0 else None)
            with col5:
                sell = stats.get('sell', 0)
                st.metric("SELL", sell, 
                         delta=f"-{sell}" if sell > 0 else None)
            with col6:
                last_update = stats.get('latest_update', 'N/A')
                if last_update != 'N/A':
                    try:
                        dt = pd.to_datetime(last_update)
                        st.metric("Last Update", dt.strftime('%H:%M:%S'))
                    except:
                        st.metric("Last Update", "N/A")
                else:
                    st.metric("Last Update", "N/A")
            
            st.markdown("---")
            
            # Charts and top performers
            if show_charts:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📊 Signal Distribution")
                    dist_chart = dashboard.create_signal_distribution_chart(signals_df)
                    if dist_chart:
                        st.plotly_chart(dist_chart, use_container_width=True)
                    else:
                        st.info("No signal distribution data available")
                
                with col2:
                    st.markdown("### 📈 Top Performers (30D Forecast)")
                    if 'forecast_30d' in signals_df.columns and 'current_price' in signals_df.columns:
                        metrics_df = signals_df.copy()
                        metrics_df = metrics_df.dropna(subset=['forecast_30d', 'current_price'])
                        
                        if not metrics_df.empty:
                            metrics_df['30d_change_pct'] = ((metrics_df['forecast_30d'] - metrics_df['current_price']) / metrics_df['current_price']) * 100
                            
                            top_bullish = metrics_df.nlargest(5, '30d_change_pct')[['symbol', 'current_price', 'forecast_30d', '30d_change_pct']]
                            top_bearish = metrics_df.nsmallest(5, '30d_change_pct')[['symbol', 'current_price', 'forecast_30d', '30d_change_pct']]
                            
                            st.markdown("**Top Bullish:**")
                            st.dataframe(
                                top_bullish.style.format({
                                    'current_price': '${:.4f}',
                                    'forecast_30d': '${:.4f}',
                                    '30d_change_pct': '{:.1f}%'
                                }).apply(
                                    lambda x: ['background-color: #E8F5E9' if v > 0 else '' for v in x] if x.name == '30d_change_pct' else [''] * len(x),
                                    axis=0
                                ),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            st.markdown("**Top Bearish:**")
                            st.dataframe(
                                top_bearish.style.format({
                                    'current_price': '${:.4f}',
                                    'forecast_30d': '${:.4f}',
                                    '30d_change_pct': '{:.1f}%'
                                }).apply(
                                    lambda x: ['background-color: #FFEBEE' if v < 0 else '' for v in x] if x.name == '30d_change_pct' else [''] * len(x),
                                    axis=0
                                ),
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info("No forecast data available")
                    else:
                        st.info("Forecast columns not found in data")
            
            st.markdown("### 📋 Recent Trading Signals")
            if not signals_df.empty:
                filtered_df = signals_df.copy()
                
                if signal_filter != "All Signals":
                    filter_map = {
                        "STRONG BUY": "strong_buy",
                        "BUY": "buy",
                        "NEUTRAL": "neutral",
                        "SELL": "sell",
                        "STRONG SELL": "strong_sell"
                    }
                    filtered_df = dashboard.filter_signals(filtered_df, filter_map[signal_filter])
                
                display_cols = ['symbol', 'current_price', 'overall_signal', 'pivot_zone', 'timestamp']
                if all(col in filtered_df.columns for col in display_cols):
                    display_df = filtered_df[display_cols].copy()
                    display_df.columns = ['Symbol', 'Current Price', 'Signal', 'Pivot Zone', 'Last Updated']
                    
                    st.dataframe(
                        display_df.style.format({'Current Price': '${:.4f}'}),
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
            else:
                st.warning("No signals available to display")
        else:
            st.info("""
            ## 📊 No Data Available
            
            To view trading signals:
            
            1. **Run locally with real data:**
               ```bash
               python update_db.py
               ```
            
            2. **Or create sample data:**
               ```bash
               python init_db.py
               ```
            
            3. **Commit database to GitHub**
            
            4. **Deploy to Streamlit Cloud**
            
            The dashboard will automatically use the latest database from GitHub.
            """)
    
    # TAB 2: ALL SIGNALS
    with tab2:
        st.markdown("<h2 class='sub-header'>📈 Detailed Trading Signals</h2>", unsafe_allow_html=True)
        
        if not signals_df.empty:
            # Search and filter
            col1, col2 = st.columns([3, 1])
            with col1:
                search_symbol = st.text_input("🔍 Search by Symbol", "", key="signals_search", 
                                            placeholder="Enter symbol name...")
            with col2:
                items_per_page = st.selectbox("Items per page", [10, 25, 50], index=0)
            
            display_df = signals_df.copy()
            
            if search_symbol:
                display_df = display_df[display_df['symbol'].str.contains(search_symbol, case=False, na=False)]
            
            # Pagination
            total_items = len(display_df)
            if total_items > 0:
                st.info(f"📋 Found {total_items} signals" + (f" matching '{search_symbol}'" if search_symbol else ""))
                
                # Display signals
                for idx, row in display_df.iterrows():
                    try:
                        symbol = row.get('symbol', 'N/A')
                        current_price = float(row.get('current_price', 0))
                        overall_signal = str(row.get('overall_signal', ''))
                        
                        # Determine CSS class
                        if 'BUY' in overall_signal.upper():
                            if 'STRONG' in overall_signal.upper():
                                css_class = 'bullish'
                                signal_icon = "🟢"
                                signal_text = "STRONG BUY"
                            else:
                                css_class = 'bullish'
                                signal_icon = "🟢"
                                signal_text = "BUY"
                        elif 'SELL' in overall_signal.upper():
                            if 'STRONG' in overall_signal.upper():
                                css_class = 'bearish'
                                signal_icon = "🔴"
                                signal_text = "STRONG SELL"
                            else:
                                css_class = 'bearish'
                                signal_icon = "🔴"
                                signal_text = "SELL"
                        else:
                            css_class = 'neutral'
                            signal_icon = "🟡"
                            signal_text = "NEUTRAL"
                        
                        with st.container():
                            st.markdown(f"""
                            <div class='signal-card {css_class}'>
                                <div style='display: flex; justify-content: space-between; align-items: center;'>
                                    <div>
                                        <h3 style='margin: 0; display: flex; align-items: center;'>
                                            {signal_icon} {symbol}
                                            <span style='margin-left: 10px; font-size: 0.9rem; color: #546E7A;'>
                                                {row.get('timestamp', 'N/A')}
                                            </span>
                                        </h3>
                                    </div>
                                    <div style='text-align: right;'>
                                        <span style='font-size: 1.5rem; font-weight: bold;'>${current_price:.4f}</span><br>
                                        <span style='font-size: 0.9rem; font-weight: 600;'>{signal_text}</span>
                                    </div>
                                </div>
                                <div style='margin-top: 15px;'>
                                    <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>
                                        <div>
                                            <strong>1H Fibonacci:</strong> {row.get('fib_15m_signal', 'N/A')}<br>
                                            <strong>ML Signal:</strong> {row.get('poly_signal', 'N/A')}<br>
                                            <strong>RSI Zone:</strong> {row.get('rsi_zone', 'N/A')}
                                        </div>
                                        <div>
                                            <strong>MACD:</strong> {row.get('macd_signal', 'N/A')}<br>
                                            <strong>Pivot Zone:</strong> {row.get('pivot_zone', 'N/A')}<br>
                                            <strong>Fib Signal:</strong> {row.get('fib_signal', 'N/A')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if show_forecasts:
                                with st.expander("📈 View Price Forecast", expanded=False):
                                    try:
                                        forecast_chart = dashboard.create_price_forecast_chart(
                                            symbol,
                                            current_price,
                                            float(row.get('forecast_1h', current_price)),
                                            float(row.get('forecast_1d', current_price)),
                                            float(row.get('forecast_7d', current_price)),
                                            float(row.get('forecast_14d', current_price)),
                                            float(row.get('forecast_30d', current_price))
                                        )
                                        st.plotly_chart(forecast_chart, use_container_width=True)
                                    except Exception as e:
                                        st.error(f"Could not create forecast chart: {e}")
                    except Exception as e:
                        continue
            else:
                st.warning(f"No signals found{' matching your search' if search_symbol else ''}")
        else:
            st.warning("No signals found in the database.")
    
    # TAB 3: STRONG SIGNALS
    with tab3:
        st.markdown("<h2 class='sub-header'>🎯 Strong Signals Focus</h2>", unsafe_allow_html=True)
        
        if not signals_df.empty:
            strong_signals = signals_df[
                signals_df['overall_signal'].str.contains('STRONG', case=False, na=False)
            ]
            
            if not strong_signals.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🟢 STRONG BUY Signals")
                    strong_buy_df = strong_signals[
                        strong_signals['overall_signal'].str.contains('BUY', case=False, na=False)
                    ]
                    
                    if not strong_buy_df.empty:
                        for _, row in strong_buy_df.iterrows():
                            try:
                                symbol = row.get('symbol', 'N/A')
                                current_price = float(row.get('current_price', 0))
                                forecast_30d = float(row.get('forecast_30d', current_price))
                                pct_change = ((forecast_30d - current_price) / current_price) * 100
                                pivot_zone = row.get('pivot_zone', 'N/A')
                                
                                st.markdown(f"""
                                <div class='signal-card bullish' style='margin-bottom: 15px;'>
                                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                                        <div>
                                            <h4 style='margin: 0;'>🟢 {symbol}</h4>
                                            <span style='font-size: 0.9rem; color: #546E7A;'>{pivot_zone}</span>
                                        </div>
                                        <div style='text-align: right;'>
                                            <span style='font-size: 1.2rem; font-weight: bold;'>${current_price:.4f}</span><br>
                                            <span style='color: #4CAF50; font-weight: 600;'>30D: {pct_change:+.1f}%</span>
                                        </div>
                                    </div>
                                    <div style='margin-top: 10px; font-size: 0.9rem;'>
                                        <strong>RSI:</strong> {row.get('rsi_zone', 'N/A')}<br>
                                        <strong>MACD:</strong> {row.get('macd_signal', 'N/A')}<br>
                                        <strong>Forecast:</strong> ${forecast_30d:.4f}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            except:
                                continue
                    else:
                        st.info("No STRONG BUY signals at the moment.")
                
                with col2:
                    st.markdown("### 🔴 STRONG SELL Signals")
                    strong_sell_df = strong_signals[
                        strong_signals['overall_signal'].str.contains('SELL', case=False, na=False)
                    ]
                    
                    if not strong_sell_df.empty:
                        for _, row in strong_sell_df.iterrows():
                            try:
                                symbol = row.get('symbol', 'N/A')
                                current_price = float(row.get('current_price', 0))
                                forecast_30d = float(row.get('forecast_30d', current_price))
                                pct_change = ((forecast_30d - current_price) / current_price) * 100
                                pivot_zone = row.get('pivot_zone', 'N/A')
                                
                                st.markdown(f"""
                                <div class='signal-card bearish' style='margin-bottom: 15px;'>
                                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                                        <div>
                                            <h4 style='margin: 0;'>🔴 {symbol}</h4>
                                            <span style='font-size: 0.9rem; color: #546E7A;'>{pivot_zone}</span>
                                        </div>
                                        <div style='text-align: right;'>
                                            <span style='font-size: 1.2rem; font-weight: bold;'>${current_price:.4f}</span><br>
                                            <span style='color: #F44336; font-weight: 600;'>30D: {pct_change:+.1f}%</span>
                                        </div>
                                    </div>
                                    <div style='margin-top: 10px; font-size: 0.9rem;'>
                                        <strong>RSI:</strong> {row.get('rsi_zone', 'N/A')}<br>
                                        <strong>MACD:</strong> {row.get('macd_signal', 'N/A')}<br>
                                        <strong>Forecast:</strong> ${forecast_30d:.4f}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            except:
                                continue
                    else:
                        st.info("No STRONG SELL signals at the moment.")
                
                # Summary metrics
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Strong Signals", len(strong_signals))
                with col2:
                    st.metric("STRONG BUY", len(strong_buy_df))
                with col3:
                    st.metric("STRONG SELL", len(strong_sell_df))
                
            else:
                st.info("No strong signals (STRONG BUY/SELL) at the moment.")
        else:
            st.warning("No signals found in the database.")
    
    # TAB 4: FORECASTS
    with tab4:
        st.markdown("<h2 class='sub-header'>📅 Price Forecasts</h2>", unsafe_allow_html=True)
        
        if not hvts_df.empty:
            st.markdown("### 📊 30-Day Forecast Comparison")
            
            forecast_df = hvts_df.copy()
            forecast_df = forecast_df.sort_values(['symbol', 'timestamp'], ascending=[True, False])
            forecast_df = forecast_df.drop_duplicates(subset=['symbol'], keep='first')
            forecast_df = forecast_df.dropna(subset=['forecast_30d', 'current_price']).copy()
            
            if not forecast_df.empty:
                forecast_df['forecast_change_30d'] = ((forecast_df['forecast_30d'] - forecast_df['current_price']) / forecast_df['current_price']) * 100
                sorted_df = forecast_df.sort_values('forecast_change_30d', ascending=False)
                
                display_df = sorted_df.head(20)
                
                fig = go.Figure()
                
                colors = ['#4CAF50' if x > 0 else '#F44336' for x in display_df['forecast_change_30d']]
                
                fig.add_trace(go.Bar(
                    x=display_df['symbol'],
                    y=display_df['forecast_change_30d'],
                    marker_color=colors,
                    text=[f"{x:.1f}%" for x in display_df['forecast_change_30d']],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Change: %{y:.1f}%<extra></extra>'
                ))
                
                fig.update_layout(
                    title='30-Day Forecast Percentage Change (Top 20)',
                    xaxis_title='Symbol',
                    yaxis_title='Forecast Change (%)',
                    template='plotly_white',
                    height=500,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 📋 Detailed Forecasts")
                
                forecast_search = st.text_input("🔍 Search Forecasts by Symbol", "", key="forecast_search")
                
                forecast_display_df = hvts_df.copy()
                forecast_display_df = forecast_display_df.sort_values(['symbol', 'timestamp'], ascending=[True, False])
                forecast_display_df = forecast_display_df.drop_duplicates(subset=['symbol'], keep='first')
                
                if forecast_search:
                    forecast_display_df = forecast_display_df[forecast_display_df['symbol'].str.contains(forecast_search, case=False, na=False)]
                
                display_cols = ['symbol', 'current_price', 'forecast_1d', 'forecast_7d', 
                              'forecast_14d', 'forecast_30d', 'poly_signal', 'timestamp']
                
                if all(col in forecast_display_df.columns for col in display_cols):
                    # Calculate percentage changes
                    display_df_with_pct = forecast_display_df.copy()
                    for period in ['1d', '7d', '14d', '30d']:
                        col_name = f'forecast_{period}'
                        pct_col = f'{period}_change_pct'
                        display_df_with_pct[pct_col] = ((display_df_with_pct[col_name] - display_df_with_pct['current_price']) / display_df_with_pct['current_price']) * 100
                    
                    st.dataframe(
                        display_df_with_pct[['symbol', 'current_price', 
                                           'forecast_1d', '1d_change_pct',
                                           'forecast_7d', '7d_change_pct',
                                           'forecast_14d', '14d_change_pct',
                                           'forecast_30d', '30d_change_pct',
                                           'poly_signal', 'timestamp']].rename(columns={
                            'symbol': 'Symbol',
                            'current_price': 'Current',
                            'forecast_1d': '1D',
                            '1d_change_pct': '1D %',
                            'forecast_7d': '7D',
                            '7d_change_pct': '7D %',
                            'forecast_14d': '14D',
                            '14d_change_pct': '14D %',
                            'forecast_30d': '30D',
                            '30d_change_pct': '30D %',
                            'poly_signal': 'ML Signal',
                            'timestamp': 'Updated'
                        }).style.format({
                            'Current': '${:.4f}',
                            '1D': '${:.4f}',
                            '1D %': '{:.1f}%',
                            '7D': '${:.4f}',
                            '7D %': '{:.1f}%',
                            '14D': '${:.4f}',
                            '14D %': '{:.1f}%',
                            '30D': '${:.4f}',
                            '30D %': '{:.1f}%'
                        }).apply(
                            lambda x: ['background-color: #E8F5E9' if v > 0 else 'background-color: #FFEBEE' if v < 0 else '' 
                                      for v in x] if x.name in ['1D %', '7D %', '14D %', '30D %'] else [''] * len(x),
                            axis=0
                        ),
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
        else:
            st.warning("No forecast data found in the database.")
    
    # TAB 5: FIBONACCI
    with tab5:
        st.markdown("<h2 class='sub-header'>📐 Fibonacci 1-Hour Indicators</h2>", unsafe_allow_html=True)
        
        if not fib_df.empty:
            st.markdown(f"""
            <div class='info-badge'>
                📊 Displaying {len(fib_df)} unique symbols with latest Fibonacci 1-hour data
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Unique Symbols", len(fib_df))
            with col2:
                bullish_count = len(fib_df[fib_df['fib_1h_signal'].str.contains('BULLISH', case=False, na=False)])
                st.metric("Bullish Signals", bullish_count)
            with col3:
                bearish_count = len(fib_df[fib_df['fib_1h_signal'].str.contains('BEARISH', case=False, na=False)])
                st.metric("Bearish Signals", bearish_count)
            with col4:
                latest_update = fib_df['timestamp'].max() if len(fib_df) > 0 else 'N/A'
                if latest_update != 'N/A':
                    try:
                        dt = pd.to_datetime(latest_update)
                        st.metric("Last Updated", dt.strftime('%H:%M:%S'))
                    except:
                        st.metric("Last Updated", latest_update)
                else:
                    st.metric("Last Updated", 'N/A')
            
            st.markdown("---")
            
            # Search
            fib_search = st.text_input("🔍 Search Fibonacci 1h Symbols", "", key="fib_search")
            
            display_fib_df = fib_df.copy()
            if fib_search:
                display_fib_df = display_fib_df[display_fib_df['symbol'].str.contains(fib_search, case=False, na=False)]
                st.info(f"Found {len(display_fib_df)} symbols matching '{fib_search}'")
            
            # Display Fibonacci data
            for _, row in display_fib_df.iterrows():
                try:
                    symbol = row.get('symbol', 'N/A')
                    current_price = float(row.get('current_price', 0))
                    fib_signal = row.get('fib_1h_signal', 'N/A')
                    
                    fib_levels = {}
                    for key in ['0', '23_6', '38_2', '50', '61_8', '78_6', '100', '127_2', '161_8', '261_8', '423_6']:
                        level_key = f'fib_level_{key}'
                        fib_levels[level_key] = row.get(level_key)
                    
                    with st.expander(f"{symbol} - ${current_price:.4f} | 1h Signal: {fib_signal}", expanded=False):
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.markdown("### 📐 Fibonacci Levels (1h)")
                            
                            st.markdown("**Retracement Levels:**")
                            retrace_cols = st.columns(3)
                            retracement_levels = [
                                ('0', '0.0%'),
                                ('23_6', '23.6%'),
                                ('38_2', '38.2%'),
                                ('50', '50.0%'),
                                ('61_8', '61.8%'),
                                ('78_6', '78.6%'),
                                ('100', '100.0%')
                            ]
                            
                            for i, (key, label) in enumerate(retracement_levels):
                                level_value = row.get(f'fib_level_{key}')
                                if pd.notna(level_value):
                                    with retrace_cols[i % 3]:
                                        st.markdown(f"""
                                        <div class='fib-level fib-retracement'>
                                            {label}: ${float(level_value):.4f}
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            st.markdown("**Extension Levels:**")
                            ext_cols = st.columns(3)
                            extension_levels = [
                                ('127_2', '127.2%'),
                                ('161_8', '161.8%'),
                                ('261_8', '261.8%'),
                                ('423_6', '423.6%')
                            ]
                            
                            for i, (key, label) in enumerate(extension_levels):
                                level_value = row.get(f'fib_level_{key}')
                                if pd.notna(level_value):
                                    with ext_cols[i % 3]:
                                        st.markdown(f"""
                                        <div class='fib-level fib-extension'>
                                            {label}: ${float(level_value):.4f}
                                        </div>
                                        """, unsafe_allow_html=True)
                        
                        with col2:
                            fib_chart = dashboard.create_fibonacci_chart(symbol, current_price, fib_levels)
                            st.plotly_chart(fib_chart, use_container_width=True)
                        
                        st.markdown(f"""
                        **Pivot Zone:** {row.get('pivot_zone', 'N/A')}  
                        **Last Updated:** {row.get('timestamp', 'N/A')}
                        """)
                
                except Exception as e:
                    continue
            
            # Data table
            st.markdown("### 📋 Fibonacci 1h Data Table")
            display_cols = ['symbol', 'current_price', 'fib_1h_signal', 'pivot_zone', 'timestamp']
            if all(col in fib_df.columns for col in display_cols):
                st.dataframe(
                    fib_df[display_cols].rename(columns={
                        'symbol': 'Symbol',
                        'current_price': 'Current Price',
                        'fib_1h_signal': 'Fib Signal (1h)',
                        'pivot_zone': 'Pivot Zone',
                        'timestamp': 'Updated'
                    }).style.format({'Current Price': '${:.4f}'}),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("No Fibonacci data found in the database.")
    
    # TAB 6: REGRESSION
    with tab6:
        st.markdown("<h2 class='sub-header'>📈 Polynomial Regression Daily Indicators</h2>", unsafe_allow_html=True)
        
        if not reg_df.empty:
            st.markdown(f"""
            <div class='info-badge'>
                📊 Displaying {len(reg_df)} unique symbols with latest Regression data
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Unique Symbols", len(reg_df))
            with col2:
                bullish_count = len(reg_df[reg_df['poly_signal_daily'].str.contains('BULLISH', case=False, na=False)])
                st.metric("Bullish Signals", bullish_count)
            with col3:
                bearish_count = len(reg_df[reg_df['poly_signal_daily'].str.contains('BEARISH', case=False, na=False)])
                st.metric("Bearish Signals", bearish_count)
            with col4:
                avg_confidence = reg_df['poly_confidence'].mean() if 'poly_confidence' in reg_df.columns else 0
                st.metric("Avg Confidence", f"{avg_confidence:.1f}%" if avg_confidence > 0 else "N/A")
            
            st.markdown("---")
            
            # Search
            reg_search = st.text_input("🔍 Search Regression Symbols", "", key="reg_search")
            
            display_reg_df = reg_df.copy()
            if reg_search:
                display_reg_df = display_reg_df[display_reg_df['symbol'].str.contains(reg_search, case=False, na=False)]
                st.info(f"Found {len(display_reg_df)} symbols matching '{reg_search}'")
            
            # Display regression data
            for _, row in display_reg_df.iterrows():
                try:
                    symbol = row.get('symbol', 'N/A')
                    current_price = float(row.get('current_price', 0))
                    reg_signal = row.get('poly_signal_daily', 'N/A')
                    confidence = row.get('poly_confidence', 0)
                    r_squared = row.get('r_squared', 0)
                    trend_strength = row.get('trend_strength', 0)
                    
                    signal_color = '#4CAF50' if 'BULLISH' in str(reg_signal).upper() else '#F44336' if 'BEARISH' in str(reg_signal).upper() else '#FF9800'
                    
                    with st.container():
                        st.markdown(f"""
                        <div class='regression-card'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h3 style='margin: 0; color: {signal_color};'>{symbol}</h3>
                                    <div style='font-size: 0.9rem; color: #546E7A;'>
                                        Updated: {row.get('timestamp', 'N/A')}
                                    </div>
                                </div>
                                <div style='text-align: right;'>
                                    <span style='font-size: 1.2rem; font-weight: bold;'>${current_price:.4f}</span><br>
                                    <span style='font-size: 0.9rem;'>Signal: <strong>{reg_signal}</strong></span>
                                </div>
                            </div>
                            <div style='margin-top: 15px;'>
                                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;'>
                                    <div>
                                        <strong>Confidence:</strong> {confidence:.1f}%<br>
                                        <strong>R² Score:</strong> {r_squared:.3f}<br>
                                        <strong>Trend Strength:</strong> {trend_strength:.1f}%
                                    </div>
                                    <div>
                                        <strong>Support:</strong> ${row.get('support_level', 0):.4f}<br>
                                        <strong>Resistance:</strong> ${row.get('resistance_level', 0):.4f}<br>
                                        <strong>1D Forecast:</strong> ${row.get('forecast_1d', 0):.4f}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if show_charts:
                            reg_chart = dashboard.create_regression_chart(
                                symbol,
                                current_price,
                                float(row.get('poly_regression_value', 0)),
                                float(row.get('support_level', current_price * 0.95)),
                                float(row.get('resistance_level', current_price * 1.05)),
                                float(row.get('forecast_1d', current_price)),
                                float(row.get('forecast_7d', current_price)),
                                float(row.get('forecast_30d', current_price))
                            )
                            st.plotly_chart(reg_chart, use_container_width=True)
                
                except Exception as e:
                    continue
            
            # Data table
            st.markdown("### 📋 Regression Data Table")
            display_cols = ['symbol', 'current_price', 'poly_signal_daily', 'poly_confidence', 
                          'r_squared', 'trend_strength', 'support_level', 'resistance_level', 'timestamp']
            
            if all(col in reg_df.columns for col in display_cols):
                st.dataframe(
                    reg_df[display_cols].rename(columns={
                        'symbol': 'Symbol',
                        'current_price': 'Current Price',
                        'poly_signal_daily': 'Regression Signal',
                        'poly_confidence': 'Confidence %',
                        'r_squared': 'R²',
                        'trend_strength': 'Trend Strength %',
                        'support_level': 'Support',
                        'resistance_level': 'Resistance',
                        'timestamp': 'Updated'
                    }).style.format({
                        'Current Price': '${:.4f}',
                        'Confidence %': '{:.1f}%',
                        'R²': '{:.3f}',
                        'Trend Strength %': '{:.1f}%',
                        'Support': '${:.4f}',
                        'Resistance': '${:.4f}'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("No regression data found in the database.")
    
    # TAB 7: EXTREME DISCOUNT
    with tab7:
        st.markdown("<h2 class='sub-header'>🔥 Extreme Discount Zone Opportunities</h2>", unsafe_allow_html=True)
        
        if not extreme_discount_df.empty:
            st.markdown("""
            <div class='extreme-discount-indicator'>
                🚀 BUYING OPPORTUNITY: These symbols are currently in EXTREME DISCOUNT ZONE
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class='discount-metric'>
                    <h3 style='margin: 0; color: #2196F3;'>{discount_stats.get('total_symbols', 0)}</h3>
                    <p style='margin: 5px 0;'>Extreme Discount Symbols</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_bullish = discount_stats.get('strong_buy', 0) + discount_stats.get('buy', 0)
                st.markdown(f"""
                <div class='discount-metric'>
                    <h3 style='margin: 0; color: #4CAF50;'>{total_bullish}</h3>
                    <p style='margin: 5px 0;'>Bullish Signals</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_gain = discount_stats.get('avg_forecast_30d_change', 0)
                color = '#4CAF50' if avg_gain > 0 else '#F44336'
                st.markdown(f"""
                <div class='discount-metric'>
                    <h3 style='margin: 0; color: {color};'>{avg_gain:+.1f}%</h3>
                    <p style='margin: 5px 0;'>Avg 30D Forecast</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_price = discount_stats.get('avg_current_price', 0)
                st.markdown(f"""
                <div class='discount-metric'>
                    <h3 style='margin: 0; color: #FF9800;'>${avg_price:.4f}</h3>
                    <p style='margin: 5px 0;'>Avg Current Price</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Chart
            if show_charts:
                st.markdown("### 📊 30-Day Potential Gains")
                discount_chart = dashboard.create_extreme_discount_chart(extreme_discount_df)
                if discount_chart:
                    st.plotly_chart(discount_chart, use_container_width=True)
            
            # Top gainers
            if discount_stats.get('top_potential_gainers'):
                st.markdown("### 🏆 Top 5 Potential Gainers")
                gainers_cols = st.columns(5)
                
                for idx, gainer in enumerate(discount_stats['top_potential_gainers'][:5]):
                    with gainers_cols[idx]:
                        symbol = gainer['symbol']
                        current_price = gainer['current_price']
                        forecast = gainer['forecast_30d']
                        change = gainer['forecast_change_30d']
                        
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); 
                                    border-radius: 10px; padding: 15px; text-align: center; 
                                    border: 2px solid #2196F3; margin: 5px;'>
                            <h4 style='margin: 0; color: #1565C0;'>{symbol}</h4>
                            <p style='margin: 5px 0; font-size: 0.9rem; color: #546E7A;'>
                                Current: ${current_price:.4f}
                            </p>
                            <p style='margin: 5px 0; font-size: 0.9rem; color: #546E7A;'>
                                Forecast: ${forecast:.4f}
                            </p>
                            <div style='background-color: #C8E6C9; color: #2E7D32; 
                                        padding: 5px; border-radius: 5px; font-weight: bold;'>
                                {change:+.1f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Search
            discount_search = st.text_input("🔍 Search Extreme Discount Symbols", "", key="discount_search")
            
            display_discount_df = extreme_discount_df.copy()
            if discount_search:
                display_discount_df = display_discount_df[display_discount_df['symbol'].str.contains(discount_search, case=False, na=False)]
                st.info(f"Found {len(display_discount_df)} extreme discount symbols matching '{discount_search}'")
            
            # Display symbols
            st.markdown(f"### 📋 Extreme Discount Symbols ({len(display_discount_df)} total)")
            
            for _, row in display_discount_df.iterrows():
                try:
                    symbol = row.get('symbol', 'N/A')
                    current_price = float(row.get('current_price', 0))
                    pivot_zone = row.get('pivot_zone', 'N/A')
                    overall_signal = row.get('overall_signal', 'N/A')
                    
                    forecast_change = None
                    if 'forecast_30d' in row and pd.notna(row['forecast_30d']):
                        forecast_30d = float(row['forecast_30d'])
                        forecast_change = ((forecast_30d - current_price) / current_price) * 100
                    
                    with st.container():
                        st.markdown(f"""
                        <div class='signal-card extreme-discount'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h3 style='margin: 0; color: #1565C0;'>{symbol}</h3>
                                    <div class='discount-badge'>EXTREME DISCOUNT ZONE</div>
                                </div>
                                <div style='text-align: right;'>
                                    <span style='font-size: 1.5rem; font-weight: bold;'>${current_price:.4f}</span><br>
                                    <span style='color: #546E7A; font-size: 0.9rem;'>{overall_signal}</span>
                                </div>
                            </div>
                            <div style='margin-top: 15px;'>
                                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;'>
                                    <div>
                                        <strong>Pivot Zone:</strong> {pivot_zone}<br>
                                        <strong>RSI Zone:</strong> {row.get('rsi_zone', 'N/A')}<br>
                                        <strong>MACD:</strong> {row.get('macd_signal', 'N/A')}
                                    </div>
                                    <div>
                                        <strong>Forecasts:</strong><br>
                                        1D: ${float(row.get('forecast_1d', current_price)):.4f}<br>
                                        7D: ${float(row.get('forecast_7d', current_price)):.4f}<br>
                                        30D: ${float(row.get('forecast_30d', current_price)):.4f}
                                        {f"<br><span style='color: #4CAF50; font-weight: bold;'>({forecast_change:+.1f}%)</span>" if forecast_change is not None else ""}
                                    </div>
                                </div>
                                <div style='margin-top: 10px; font-size: 0.9rem; color: #546E7A;'>
                                    <strong>Updated:</strong> {row.get('timestamp', 'N/A')}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if show_forecasts:
                            try:
                                forecast_chart = dashboard.create_price_forecast_chart(
                                    symbol,
                                    current_price,
                                    float(row.get('forecast_1h', current_price)),
                                    float(row.get('forecast_1d', current_price)),
                                    float(row.get('forecast_7d', current_price)),
                                    float(row.get('forecast_14d', current_price)),
                                    float(row.get('forecast_30d', current_price))
                                )
                                st.plotly_chart(forecast_chart, use_container_width=True)
                            except:
                                pass
                
                except:
                    continue
            
            # Data table
            st.markdown("### 📊 Extreme Discount Data Table")
            display_cols = ['symbol', 'current_price', 'pivot_zone', 'overall_signal', 
                          'forecast_1d', 'forecast_7d', 'forecast_30d', 'timestamp']
            
            if all(col in display_discount_df.columns for col in display_cols):
                table_df = display_discount_df[display_cols].copy()
                table_df['30d_change_pct'] = ((table_df['forecast_30d'] - table_df['current_price']) / table_df['current_price']) * 100
                
                st.dataframe(
                    table_df.rename(columns={
                        'symbol': 'Symbol',
                        'current_price': 'Current Price',
                        'pivot_zone': 'Pivot Zone',
                        'overall_signal': 'Signal',
                        'forecast_1d': '1D Forecast',
                        'forecast_7d': '7D Forecast',
                        'forecast_30d': '30D Forecast',
                        '30d_change_pct': '30D Change %',
                        'timestamp': 'Updated'
                    }).style.format({
                        'Current Price': '${:.4f}',
                        '1D Forecast': '${:.4f}',
                        '7D Forecast': '${:.4f}',
                        '30D Forecast': '${:.4f}',
                        '30D Change %': '{:.1f}%'
                    }).apply(
                        lambda x: ['background-color: #E8F5E9' if v > 0 else 'background-color: #FFEBEE' 
                                  for v in x] if x.name == '30D Change %' else [''] * len(x),
                        axis=0
                    ),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("No symbols currently in Extreme Discount Zone.")
            st.info("""
            **What is Extreme Discount Zone?**
            
            The Extreme Discount Zone identifies symbols where the current price is 
            significantly below its historical support levels, potentially indicating 
            oversold conditions and buying opportunities.
            
            Check back regularly as market conditions change!
            """)
    
    # TAB 8: PORTFOLIO
    with tab8:
        st.markdown("<h2 class='sub-header'>💰 Portfolio: Bullish Regression + Extreme Discount</h2>", unsafe_allow_html=True)
        
        if not portfolio_df.empty:
            st.markdown("""
            <div class='portfolio-indicator'>
                💰 PORTFOLIO OPPORTUNITY: Bullish Daily Regression + Extreme Discount Zone
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class='portfolio-metric'>
                    <h3 style='margin: 0; color: #4CAF50;'>{portfolio_stats.get('total_symbols', 0)}</h3>
                    <p style='margin: 5px 0;'>Portfolio Symbols</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_gain = portfolio_stats.get('avg_forecast_30d_change', 0)
                color = '#4CAF50' if avg_gain > 0 else '#F44336'
                st.markdown(f"""
                <div class='portfolio-metric'>
                    <h3 style='margin: 0; color: {color};'>{avg_gain:+.1f}%</h3>
                    <p style='margin: 5px 0;'>Avg 30D Forecast</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_price = portfolio_stats.get('avg_current_price', 0)
                st.markdown(f"""
                <div class='portfolio-metric'>
                    <h3 style='margin: 0; color: #FF9800;'>${avg_price:.4f}</h3>
                    <p style='margin: 5px 0;'>Avg Current Price</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                # Download button for portfolio
                filename, csv_content = dashboard.save_portfolio_csv(portfolio_df)
                if csv_content:
                    st.download_button(
                        label="📥 Download Portfolio CSV",
                        data=csv_content,
                        file_name=filename,
                        mime="text/csv",
                        use_container_width=True
                    )
            
            st.markdown("---")
            
            # Portfolio symbols in CSV format
            st.markdown("### 📋 Portfolio Symbols (CSV Format)")
            portfolio_csv = dashboard.get_portfolio_symbols_csv(portfolio_df)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.code(portfolio_csv, language="csv")
            
            with col2:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.write("📋 Copied to clipboard! Paste in your trading platform.")
            
            # Top gainers
            if portfolio_stats.get('top_potential_gainers'):
                st.markdown("### 🏆 Top Portfolio Gainers")
                gainers_cols = st.columns(5)
                
                for idx, gainer in enumerate(portfolio_stats['top_potential_gainers'][:5]):
                    with gainers_cols[idx]:
                        symbol = gainer['symbol']
                        current_price = gainer['current_price']
                        forecast = gainer['forecast_30d']
                        change = gainer['forecast_change_30d']
                        
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); 
                                    border-radius: 10px; padding: 15px; text-align: center; 
                                    border: 2px solid #2196F3; margin: 5px;'>
                            <h4 style='margin: 0; color: #1565C0;'>{symbol}</h4>
                            <p style='margin: 5px 0; font-size: 0.9rem; color: #546E7A;'>
                                Current: ${current_price:.4f}
                            </p>
                            <p style='margin: 5px 0; font-size: 0.9rem; color: #546E7A;'>
                                Forecast: ${forecast:.4f}
                            </p>
                            <div style='background-color: #C8E6C9; color: #2E7D32; 
                                        padding: 5px; border-radius: 5px; font-weight: bold;'>
                                {change:+.1f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Portfolio details
            st.markdown(f"### 🔍 Portfolio Details ({len(portfolio_df)} symbols)")
            
            portfolio_search = st.text_input("🔍 Search Portfolio Symbols", "", key="portfolio_search")
            
            display_portfolio_df = portfolio_df.copy()
            if portfolio_search:
                display_portfolio_df = display_portfolio_df[display_portfolio_df['symbol'].str.contains(portfolio_search, case=False, na=False)]
                st.info(f"Found {len(display_portfolio_df)} portfolio symbols matching '{portfolio_search}'")
            
            for _, row in display_portfolio_df.iterrows():
                try:
                    symbol = row.get('symbol', 'N/A')
                    current_price = float(row.get('current_price', 0))
                    pivot_zone = row.get('pivot_zone', 'N/A')
                    overall_signal = row.get('overall_signal', 'N/A')
                    
                    forecast_change = None
                    if 'forecast_30d' in row and pd.notna(row['forecast_30d']):
                        forecast_30d = float(row['forecast_30d'])
                        forecast_change = ((forecast_30d - current_price) / current_price) * 100
                    
                    with st.container():
                        st.markdown(f"""
                        <div class='signal-card portfolio'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h3 style='margin: 0; color: #1565C0;'>{symbol}</h3>
                                    <div class='portfolio-badge'>PORTFOLIO: Bullish Regression + Extreme Discount</div>
                                </div>
                                <div style='text-align: right;'>
                                    <span style='font-size: 1.5rem; font-weight: bold;'>${current_price:.4f}</span><br>
                                    <span style='color: #546E7A; font-size: 0.9rem;'>{overall_signal}</span>
                                </div>
                            </div>
                            <div style='margin-top: 15px;'>
                                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;'>
                                    <div>
                                        <strong>Pivot Zone:</strong> {pivot_zone}<br>
                                        <strong>RSI Zone:</strong> {row.get('rsi_zone', 'N/A')}<br>
                                        <strong>MACD:</strong> {row.get('macd_signal', 'N/A')}
                                    </div>
                                    <div>
                                        <strong>Forecasts:</strong><br>
                                        1D: ${float(row.get('forecast_1d', current_price)):.4f}<br>
                                        7D: ${float(row.get('forecast_7d', current_price)):.4f}<br>
                                        30D: ${float(row.get('forecast_30d', current_price)):.4f}
                                        {f"<br><span style='color: #4CAF50; font-weight: bold;'>({forecast_change:+.1f}%)</span>" if forecast_change is not None else ""}
                                    </div>
                                </div>
                                <div style='margin-top: 10px; font-size: 0.9rem; color: #546E7A;'>
                                    <strong>Updated:</strong> {row.get('timestamp', 'N/A')}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if show_forecasts:
                            try:
                                forecast_chart = dashboard.create_price_forecast_chart(
                                    symbol,
                                    current_price,
                                    float(row.get('forecast_1h', current_price)),
                                    float(row.get('forecast_1d', current_price)),
                                    float(row.get('forecast_7d', current_price)),
                                    float(row.get('forecast_14d', current_price)),
                                    float(row.get('forecast_30d', current_price))
                                )
                                st.plotly_chart(forecast_chart, use_container_width=True)
                            except:
                                pass
                
                except:
                    continue
            
            # Data table
            st.markdown("### 📊 Portfolio Data Table")
            display_cols = ['symbol', 'current_price', 'pivot_zone', 'overall_signal', 
                          'forecast_1d', 'forecast_7d', 'forecast_30d', 'timestamp']
            
            if all(col in display_portfolio_df.columns for col in display_cols):
                table_df = display_portfolio_df[display_cols].copy()
                table_df['30d_change_pct'] = ((table_df['forecast_30d'] - table_df['current_price']) / table_df['current_price']) * 100
                
                st.dataframe(
                    table_df.rename(columns={
                        'symbol': 'Symbol',
                        'current_price': 'Current Price',
                        'pivot_zone': 'Pivot Zone',
                        'overall_signal': 'Signal',
                        'forecast_1d': '1D Forecast',
                        'forecast_7d': '7D Forecast',
                        'forecast_30d': '30D Forecast',
                        '30d_change_pct': '30D Change %',
                        'timestamp': 'Updated'
                    }).style.format({
                        'Current Price': '${:.4f}',
                        '1D Forecast': '${:.4f}',
                        '7D Forecast': '${:.4f}',
                        '30D Forecast': '${:.4f}',
                        '30D Change %': '{:.1f}%'
                    }).apply(
                        lambda x: ['background-color: #E8F5E9' if v > 0 else 'background-color: #FFEBEE' 
                                  for v in x] if x.name == '30D Change %' else [''] * len(x),
                        axis=0
                    ),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("No portfolio symbols found (Bullish Regression + Extreme Discount).")
            st.info("""
            **Portfolio Criteria:**
            
            This portfolio shows symbols that meet BOTH conditions:
            1. **Bullish Polynomial Regression** on Daily timeframe
            2. **Price in Extreme Discount Zone**
            
            These symbols represent potential buying opportunities with strong 
            technical indicators supporting upward movement.
            
            Check back regularly as market conditions change!
            """)
    
    # TAB 9: OVERVALUED
    with tab9:
        st.markdown("<h2 class='sub-header'>⚠️ Overvalued: Above Buy Zone</h2>", unsafe_allow_html=True)
        
        if not overvalued_df.empty:
            st.markdown("""
            <div class='overvalued-indicator'>
                ⚠️ CAUTION: These symbols are currently in ABOVE BUY ZONE
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class='overvalued-metric'>
                    <h3 style='margin: 0; color: #FF9800;'>{overvalued_stats.get('total_symbols', 0)}</h3>
                    <p style='margin: 5px 0;'>Overvalued Symbols</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_bearish = overvalued_stats.get('strong_sell', 0) + overvalued_stats.get('sell', 0)
                st.markdown(f"""
                <div class='overvalued-metric'>
                    <h3 style='margin: 0; color: #F44336;'>{total_bearish}</h3>
                    <p style='margin: 5px 0;'>Bearish Signals</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_change = overvalued_stats.get('avg_forecast_30d_change', 0)
                color = '#4CAF50' if avg_change > 0 else '#F44336'
                st.markdown(f"""
                <div class='overvalued-metric'>
                    <h3 style='margin: 0; color: {color};'>{avg_change:+.1f}%</h3>
                    <p style='margin: 5px 0;'>Avg 30D Forecast</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_price = overvalued_stats.get('avg_current_price', 0)
                st.markdown(f"""
                <div class='overvalued-metric'>
                    <h3 style='margin: 0; color: #FF5722;'>${avg_price:.4f}</h3>
                    <p style='margin: 5px 0;'>Avg Current Price</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Chart
            if show_charts:
                st.markdown("### 📊 30-Day Potential Changes")
                overvalued_chart = dashboard.create_overvalued_chart(overvalued_df)
                if overvalued_chart:
                    st.plotly_chart(overvalued_chart, use_container_width=True)
            
            # Top decliners
            if overvalued_stats.get('top_potential_decliners'):
                st.markdown("### 📉 Top 5 Potential Decliners")
                decliners_cols = st.columns(5)
                
                for idx, decliner in enumerate(overvalued_stats['top_potential_decliners'][:5]):
                    with decliners_cols[idx]:
                        symbol = decliner['symbol']
                        current_price = decliner['current_price']
                        forecast = decliner['forecast_30d']
                        change = decliner['forecast_change_30d']
                        
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%); 
                                    border-radius: 10px; padding: 15px; text-align: center; 
                                    border: 2px solid #F44336; margin: 5px;'>
                            <h4 style='margin: 0; color: #C62828;'>{symbol}</h4>
                            <p style='margin: 5px 0; font-size: 0.9rem; color: #546E7A;'>
                                Current: ${current_price:.4f}
                            </p>
                            <p style='margin: 5px 0; font-size: 0.9rem; color: #546E7A;'>
                                Forecast: ${forecast:.4f}
                            </p>
                            <div style='background-color: #FFCDD2; color: #C62828; 
                                        padding: 5px; border-radius: 5px; font-weight: bold;'>
                                {change:+.1f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Search
            overvalued_search = st.text_input("🔍 Search Overvalued Symbols", "", key="overvalued_search")
            
            display_overvalued_df = overvalued_df.copy()
            if overvalued_search:
                display_overvalued_df = display_overvalued_df[display_overvalued_df['symbol'].str.contains(overvalued_search, case=False, na=False)]
                st.info(f"Found {len(display_overvalued_df)} overvalued symbols matching '{overvalued_search}'")
            
            # Display symbols
            st.markdown(f"### 📋 Overvalued Symbols ({len(display_overvalued_df)} total)")
            
            for _, row in display_overvalued_df.iterrows():
                try:
                    symbol = row.get('symbol', 'N/A')
                    current_price = float(row.get('current_price', 0))
                    pivot_zone = row.get('pivot_zone', 'N/A')
                    overall_signal = row.get('overall_signal', 'N/A')
                    
                    forecast_change = None
                    if 'forecast_30d' in row and pd.notna(row['forecast_30d']):
                        forecast_30d = float(row['forecast_30d'])
                        forecast_change = ((forecast_30d - current_price) / current_price) * 100
                    
                    with st.container():
                        st.markdown(f"""
                        <div class='signal-card overvalued'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h3 style='margin: 0; color: #EF6C00;'>{symbol}</h3>
                                    <div class='overvalued-badge'>ABOVE BUY ZONE - CAUTION</div>
                                </div>
                                <div style='text-align: right;'>
                                    <span style='font-size: 1.5rem; font-weight: bold;'>${current_price:.4f}</span><br>
                                    <span style='color: #546E7A; font-size: 0.9rem;'>{overall_signal}</span>
                                </div>
                            </div>
                            <div style='margin-top: 15px;'>
                                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;'>
                                    <div>
                                        <strong>Pivot Zone:</strong> {pivot_zone}<br>
                                        <strong>RSI Zone:</strong> {row.get('rsi_zone', 'N/A')}<br>
                                        <strong>MACD:</strong> {row.get('macd_signal', 'N/A')}
                                    </div>
                                    <div>
                                        <strong>Forecasts:</strong><br>
                                        1D: ${float(row.get('forecast_1d', current_price)):.4f}<br>
                                        7D: ${float(row.get('forecast_7d', current_price)):.4f}<br>
                                        30D: ${float(row.get('forecast_30d', current_price)):.4f}
                                        {f"<br><span style='color: #F44336; font-weight: bold;'>({forecast_change:+.1f}%)</span>" if forecast_change is not None else ""}
                                    </div>
                                </div>
                                <div style='margin-top: 10px; font-size: 0.9rem; color: #546E7A;'>
                                    <strong>Updated:</strong> {row.get('timestamp', 'N/A')}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if show_forecasts:
                            try:
                                forecast_chart = dashboard.create_price_forecast_chart(
                                    symbol,
                                    current_price,
                                    float(row.get('forecast_1h', current_price)),
                                    float(row.get('forecast_1d', current_price)),
                                    float(row.get('forecast_7d', current_price)),
                                    float(row.get('forecast_14d', current_price)),
                                    float(row.get('forecast_30d', current_price))
                                )
                                st.plotly_chart(forecast_chart, use_container_width=True)
                            except:
                                pass
                
                except:
                    continue
            
            # Data table
            st.markdown("### 📊 Overvalued Data Table")
            display_cols = ['symbol', 'current_price', 'pivot_zone', 'overall_signal', 
                          'forecast_1d', 'forecast_7d', 'forecast_30d', 'timestamp']
            
            if all(col in display_overvalued_df.columns for col in display_cols):
                table_df = display_overvalued_df[display_cols].copy()
                table_df['30d_change_pct'] = ((table_df['forecast_30d'] - table_df['current_price']) / table_df['current_price']) * 100
                
                st.dataframe(
                    table_df.rename(columns={
                        'symbol': 'Symbol',
                        'current_price': 'Current Price',
                        'pivot_zone': 'Pivot Zone',
                        'overall_signal': 'Signal',
                        'forecast_1d': '1D Forecast',
                        'forecast_7d': '7D Forecast',
                        'forecast_30d': '30D Forecast',
                        '30d_change_pct': '30D Change %',
                        'timestamp': 'Updated'
                    }).style.format({
                        'Current Price': '${:.4f}',
                        '1D Forecast': '${:.4f}',
                        '7D Forecast': '${:.4f}',
                        '30D Forecast': '${:.4f}',
                        '30D Change %': '{:.1f}%'
                    }).apply(
                        lambda x: ['background-color: #E8F5E9' if v > 0 else 'background-color: #FFEBEE' 
                                  for v in x] if x.name == '30D Change %' else [''] * len(x),
                        axis=0
                    ),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("No symbols currently in Above Buy Zone.")
            st.info("""
            **What is Above Buy Zone?**
            
            The Above Buy Zone identifies symbols where the current price is 
            significantly above its historical resistance levels, potentially indicating 
            overbought conditions and selling opportunities.
            
            These symbols may be due for a price correction.
            
            Check back regularly as market conditions change!
            """)
    
    # Manual refresh button (safe for Streamlit Cloud)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Refresh Dashboard Data", type="primary", use_container_width=True):
            st.rerun()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.markdown(
            f"""
            <div style='text-align: center; color: #546E7A; font-size: 0.9rem;'>
                📊 HVTS Trading Signals Dashboard • Data from Gate.io • 
                Current time: {current_time}<br>
                <span style='font-size: 0.8rem; color: #78909C;'>
                    Note: On Streamlit Cloud, database is read-only. Update locally and commit to GitHub.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()