"""
Exchange Rate Service
Handles fetching and processing of currency exchange rates
"""
import base64
import io
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from dataclasses import dataclass

import pytz
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib
matplotlib.use('Agg')

from ..models import ExchangeRate

logger = logging.getLogger(__name__)


@dataclass
class ExchangeRateData:
    """Data class for exchange rate information"""
    graph_data: str  # Base64 encoded graph image
    latest_rate: float  # Most recent exchange rate
    last_updated: str  # Timestamp of last update


class ExchangeRateService:
    """Service for managing exchange rate data and operations"""

    TIMEZONE = 'Asia/Taipei'
    LOOKBACK_DAYS = 365

    @classmethod
    def get_exchange_rate_data(
        cls,
        currency_pair: str = 'TWDJPY',
        days: int = None
    ) -> Optional[List[ExchangeRate]]:
        """
        Fetch exchange rate data from Yahoo Finance and store in database

        Args:
            currency_pair: Currency pair code (e.g., 'TWDJPY')
            days: Number of days to fetch (default: 365)

        Returns:
            List of ExchangeRate objects or None if fetch fails
        """
        try:
            days = days or cls.LOOKBACK_DAYS

            # Set up date range
            tz = pytz.timezone(cls.TIMEZONE)
            end = datetime.now(tz).date()
            start = end - timedelta(days=days)

            # Download data from Yahoo Finance
            ticker = f'{currency_pair}=X'
            df = yf.download(ticker, start=start, end=end)

            if df.empty:
                logger.warning(f"No data returned for {currency_pair}")
                return None

            # Clear existing data for this date range
            ExchangeRate.objects.filter(
                currency_pair=currency_pair,
                date__gte=start
            ).delete()

            # Prepare bulk create list
            bulk_create_list = []
            for index, row in df.iterrows():
                # Handle timezone conversion
                if isinstance(index, pd.Timestamp):
                    if index.tz is None:
                        date = index.tz_localize('UTC').tz_convert(cls.TIMEZONE).date()
                    else:
                        date = index.tz_convert(cls.TIMEZONE).date()
                else:
                    date = index.date()

                # Extract rate value
                if isinstance(row['Close'], pd.Series):
                    rate = float(row['Close'].iloc[0])
                else:
                    rate = float(row['Close'])

                bulk_create_list.append(
                    ExchangeRate(
                        date=date,
                        rate=rate,
                        currency_pair=currency_pair
                    )
                )

            if not bulk_create_list:
                logger.warning(f"No valid data to save for {currency_pair}")
                return None

            # Bulk create records
            ExchangeRate.objects.bulk_create(bulk_create_list)

            # Return saved records
            return ExchangeRate.objects.filter(
                currency_pair=currency_pair,
                date__gte=start
            ).order_by('date')

        except Exception as e:
            logger.error(f"Error fetching exchange rate data: {e}", exc_info=True)
            return None

    @classmethod
    def convert_currency(
        cls,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Optional[dict]:
        """
        Convert amount from one currency to another

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Dictionary with conversion results or None if failed
        """
        try:
            # Same currency - no conversion needed
            if from_currency == to_currency:
                tz = pytz.timezone(cls.TIMEZONE)
                current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                return {
                    'result': amount,
                    'rate': 1.0,
                    'formatted_result': f"{amount:,.2f} {to_currency}",
                    'formatted_rate': f"1 {from_currency} = 1.0000 {to_currency}",
                    'conversion_time': current_time
                }

            # Get exchange rate from Yahoo Finance
            ticker = f"{from_currency}{to_currency}=X"
            df = yf.download(ticker, period="1d")

            if df.empty:
                logger.warning(f"No exchange rate data for {ticker}")
                return None

            # Calculate conversion
            current_rate = float(df['Close'].iloc[-1])
            result = amount * current_rate

            # Get current time
            tz = pytz.timezone(cls.TIMEZONE)
            current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            return {
                'result': round(result, 2),
                'rate': round(current_rate, 4),
                'formatted_result': f"{amount:,.2f} {from_currency} = {result:,.2f} {to_currency}",
                'formatted_rate': f"1 {from_currency} = {current_rate:.4f} {to_currency}",
                'conversion_time': current_time
            }

        except Exception as e:
            logger.error(f"Currency conversion error: {e}", exc_info=True)
            return None


class GraphService:
    """Service for generating exchange rate graphs"""

    TIMEZONE = 'Asia/Taipei'
    FIGURE_SIZE = (10, 5)
    DPI = 100

    @classmethod
    def generate_graph(
        cls,
        rates: List[ExchangeRate],
        title: str = None
    ) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """
        Generate a graph from exchange rate data

        Args:
            rates: List of ExchangeRate objects
            title: Optional custom title for the graph

        Returns:
            Tuple of (base64_graph, latest_rate, timestamp) or (None, None, None)
        """
        buffer = None

        try:
            # Clear any existing plots
            plt.clf()
            plt.close('all')

            # Create figure
            fig, ax = plt.subplots(figsize=cls.FIGURE_SIZE, dpi=cls.DPI)

            # Get timezone and current time
            tz = pytz.timezone(cls.TIMEZONE)
            current_datetime = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            # Extract data
            dates = [rate.date for rate in rates]
            values = [
                float(rate.rate.iloc[0]) if isinstance(rate.rate, pd.Series) else rate.rate
                for rate in rates
            ]

            # Get currency pair info
            currency_pair = rates[0].currency_pair if rates else 'Currency'
            display_title = title or f'{currency_pair} Exchange Rate'

            # Plot data
            ax.plot(dates, values, label=currency_pair, color='#4CAF50', linewidth=2)
            ax.set_title(display_title, fontsize=14, pad=20)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel(f'Exchange Rate ({currency_pair})', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend(loc='upper right')

            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            plt.tight_layout()

            # Get latest rate
            latest_rate = values[-1]

            # Add annotations
            plt.figtext(
                0.05, 0.95,
                f'Latest: {latest_rate:.4f}',
                fontsize=12,
                ha='left',
                va='top'
            )
            plt.figtext(
                0.95, 0.02,
                f'Last updated: {current_datetime} (TST)',
                fontsize=10,
                ha='right'
            )

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=cls.DPI)
            buffer.seek(0)
            graph = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return graph, latest_rate, current_datetime

        except Exception as e:
            logger.error(f"Error generating graph: {e}", exc_info=True)
            return None, None, None

        finally:
            # Clean up
            plt.close('all')
            if buffer:
                buffer.close()
