import os
import json
import re
import logging
from pathlib import Path
from datetime import datetime

import yfinance as yf
import requests_cache
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from xai_sdk import Client
from xai_sdk.chat import user, system
from xai_sdk.tools import web_search
from prompt import generate_prompt

# --- Configuration & Setup ---
load_dotenv()

# Item 9: Path Handling - Use absolute paths
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = BASE_DIR / ".cache"

# Item 7: Dependency Stability - yfinance Caching
# Install a cache for requests (used by yfinance) to prevent rate limiting on repeated runs
requests_cache.install_cache(str(CACHE_DIR / "yfinance_cache"), expire_after=3600)

# Configure Logging (Part of robustness, replacing simple prints where appropriate or adding structure)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def sanitize_filename(name: str) -> str:
    """Item 5: Output Management - Safe Filenames"""
    # Remove characters that are unsafe for filenames
    return re.sub(r'[^\w\-\.]', '_', name)

# Item 2: Enhanced Error Handling & Retries
# Retry on any Exception for demonstration, but ideally should be specific API connection errors.
# We'll rely on the SDK raising exceptions for network issues.
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def generate_report_with_retry(chat_interface):
    logger.info("Requesting report generation from Grok...")
    return chat_interface.sample()

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Input
    ticker = input("Enter a stock ticker symbol (e.g., AAPL, SAP.DE, BP.L): ").strip().upper()
    if not ticker:
        logger.error("No ticker provided. Exiting.")
        return

    # Fetch market data via yfinance
    market_data_str = None
    try:
        logger.info(f"Fetching real-time data for {ticker} via yfinance...")
        stock = yf.Ticker(ticker)
        # Accessing info triggers the fetch
        info = stock.info
        
        # Check if we got valid data
        if info and ('regularMarketPrice' in info or 'currentPrice' in info):
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            currency = info.get('currency', 'USD')
            mkt_cap = info.get('marketCap', 'N/A')
            pe_ratio = info.get('trailingPE', 'N/A')
            fwd_pe = info.get('forwardPE', 'N/A')
            company_name = info.get('longName') or info.get('shortName') or ticker

            market_data_str = f"""
                [VERIFIED REAL-TIME MARKET DATA - {today}]
                Company Name: {company_name}
                Current Price: {price} {currency}
                Market Cap: {mkt_cap}
                Trailing P/E: {pe_ratio}
                Forward P/E: {fwd_pe}
                52 Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}
                52 Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}
                """
            logger.info(f"Found: {company_name} | Price: {price} {currency}")

        else:
            logger.warning("Could not retrieve detailed market data (ticker might be invalid or data unavailable).")
    
    except Exception as e:
        # Item 2: Enhanced Error Handling - Graceful Degradation
        logger.warning(f"yfinance fetch failed: {e}")
        logger.warning("Proceeding with web-only search. The report will rely on the AI's web search capabilities.")

    # Prepare Prompt & Client
    prompt = generate_prompt(ticker, market_data=market_data_str)
    
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        logger.critical("XAI_API_KEY not found in environment variables.")
        return

    try:
        client = Client(
            api_key=api_key,
            timeout=3600,  # Override default timeout for reasoning models
        )
        chat = client.chat.create(
            model="grok-4-1-fast-reasoning",
            tools=[web_search()]
        )
        chat.append(system(f"You are Grok, a highly intelligent hedge fund analyst. You're aware that today is {today}."))
        chat.append(user(prompt))
        
        # Execute with Retry logic
        response = generate_report_with_retry(chat)
        
        logger.info("REPORT COMPLETED. SAVING TO FILE...")

        # Item 5: Output Management - Metadata & Safe Filenames
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_ticker = sanitize_filename(ticker)
        
        base_filename = f"{safe_ticker}-{timestamp_str}"
        report_path = RESULTS_DIR / f"{base_filename}.txt"
        meta_path = RESULTS_DIR / f"{base_filename}.json"

        # Write Report
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(response.content)
        
        # Write Metadata
        metadata = {
            "ticker": ticker,
            "timestamp": timestamp_str,
            "model": "grok-4-1-fast-reasoning",
            "yfinance_data_found": market_data_str is not None,
            "data_source": "yfinance + web_search" if market_data_str else "web_search_only"
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Report saved to: {report_path}")
        logger.info(f"Metadata saved to: {meta_path}")

    except Exception as e:
        logger.error(f"Critical error during report generation: {e}")

if __name__ == "__main__":
    main()