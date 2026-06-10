import pytest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from publisher.publisher import fetch_stock_data

def test_fetch_stock_data_returns_dict():
    """Vérifie que fetch_stock_data retourne un dict avec les bonnes clés"""
    with patch('publisher.publisher.yf.Ticker') as mock_ticker:
        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.iloc.__getitem__.return_value = {
            'Open': 200.0, 'High': 205.0, 'Low': 198.0,
            'Close': 203.0, 'Volume': 1000000
        }
        mock_ticker.return_value.history.return_value = mock_df

        result = fetch_stock_data("AAPL")

        assert result is not None
        assert result['ticker'] == 'AAPL'
        assert 'close' in result
        assert 'daily_return' in result
        assert 'timestamp' in result

def test_fetch_stock_data_empty_returns_none():
    """Vérifie que si Yahoo Finance retourne vide → None"""
    with patch('publisher.publisher.yf.Ticker') as mock_ticker:
        mock_df = MagicMock()
        mock_df.empty = True
        mock_ticker.return_value.history.return_value = mock_df

        result = fetch_stock_data("AAPL")
        assert result is None

def test_daily_return_calculation():
    """Vérifie que le daily_return est calculé correctement"""
    with patch('publisher.publisher.yf.Ticker') as mock_ticker:
        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.iloc.__getitem__.return_value = {
            'Open': 100.0, 'High': 110.0, 'Low': 95.0,
            'Close': 110.0, 'Volume': 500000
        }
        mock_ticker.return_value.history.return_value = mock_df

        result = fetch_stock_data("GOOGL")
        # (110 - 100) / 100 * 100 = 10%
        assert result['daily_return'] == 10.0