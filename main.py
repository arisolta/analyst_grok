import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
import requests_cache

from dotenv import load_dotenv
from agents.data_scout import DataScout
from agents.workers import FundamentalAnalyst, SentimentAnalyst, PortfolioManager, Editor

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = BASE_DIR / ".cache"

# Enable caching for yfinance
requests_cache.install_cache(str(CACHE_DIR / "yfinance_cache"), expire_after=3600)

def sanitize_filename(name: str) -> str:
    import re
    return re.sub(r'[^\w\-\.]', '_', name)

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent AI Equity Analyst")
    parser.add_argument("ticker", nargs="?", help="Stock ticker symbol (e.g., AAPL)")
    args = parser.parse_args()

    # handle interactive mode if no arg provided
    if args.ticker:
        ticker = args.ticker.strip().upper()
    else:
        ticker = input("Enter a stock ticker symbol (e.g., AAPL): ").strip().upper()

    if not ticker:
        logger.error("No ticker provided. Exiting.")
        return

    start_time = datetime.now()
    timestamp_str = start_time.strftime("%Y-%m-%d_%H-%M-%S")
    
    logger.info(f"Starting analysis for {ticker}...")

    try:
        # 1. Data Scout
        logger.info("--- Step 1: Data Scout ---")
        scout = DataScout(ticker)
        raw_data = scout.gather_all()
        
        if "error" in raw_data['market_data']:
             logger.warning(f"Data Scout reported issues: {raw_data['market_data']['error']}")
        
        # 2. Fundamental Analysis
        logger.info("--- Step 2: Fundamental Analyst ---")
        fund_analyst = FundamentalAnalyst(ticker)
        fund_report = fund_analyst.run(raw_data['financials'], raw_data['market_data'], raw_data['peer_data'])
        
        # 3. Sentiment Analysis
        logger.info("--- Step 3: Sentiment Analyst ---")
        sent_analyst = SentimentAnalyst(ticker)
        sent_report = sent_analyst.run(raw_data['news'], raw_data['market_data'])
        
        # 4. Portfolio Manager
        logger.info("--- Step 4: Portfolio Manager ---")
        pm = PortfolioManager(ticker)
        pm_verdict = pm.run(fund_report, sent_report, raw_data['market_data'])
        
        # 5. Editor
        logger.info("--- Step 5: Editor ---")
        editor = Editor(ticker)
        sections = {
            "Financial Deep Dive": fund_report,
            "Qualitative & Catalyst Analysis": sent_report,
            "Executive Summary & Investment Verdict": pm_verdict
        }
        final_report = editor.run(sections)
        
        # Save Results
        safe_ticker = sanitize_filename(ticker)
        base_filename = f"{safe_ticker}-{timestamp_str}"
        report_path = RESULTS_DIR / f"{base_filename}.md" # Changed to .md as it is markdown
        meta_path = RESULTS_DIR / f"{base_filename}.json"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(final_report)
            
        # Save Metadata (including intermediate steps for debugging)
        metadata = {
            "ticker": ticker,
            "timestamp": timestamp_str,
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "data_source": "yfinance",
            "intermediate_outputs": {
                "fundamental_analysis": fund_report,
                "sentiment_analysis": sent_report,
                "pm_verdict": pm_verdict
            },
             "raw_data_snapshot": raw_data
        }
        
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, default=str)
            
        logger.info(f"Analysis Complete! Report saved to: {report_path}")

    except Exception as e:
        logger.error(f"Critical error in orchestration: {e}", exc_info=True)

if __name__ == "__main__":
    main()
