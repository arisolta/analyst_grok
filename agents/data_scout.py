import yfinance as yf
import logging
import re
from datetime import datetime
from agents.utils import query_llm
from xai_sdk.tools import web_search

logger = logging.getLogger(__name__)

class DataScout:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
    
    def get_market_data(self) -> dict:
        """Fetches basic price and market cap data."""
        logger.info(f"Scouting market data for {self.ticker}...")
        try:
            info = self.stock.info
            # Fallback keys in case yfinance changes structure or data is missing
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if not price:
                logger.warning(f"Could not find price for {self.ticker}")
                return {"error": "Price not found"}

            return {
                "company_name": info.get('longName') or info.get('shortName') or self.ticker,
                "current_price": price,
                "currency": info.get('currency', 'USD'),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "fwd_pe": info.get('forwardPE', 'N/A'),
                "peg_ratio": info.get('pegRatio', 'N/A'),
                "beta": info.get('beta', 'N/A'),
                "52w_high": info.get('fiftyTwoWeekHigh', 'N/A'),
                "52w_low": info.get('fiftyTwoWeekLow', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "website": info.get('website', 'N/A'),
                "description": info.get('longBusinessSummary', 'N/A')
            }
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return {"error": str(e)}

    def get_financials(self) -> dict:
        """Fetches income statement and balance sheet data."""
        logger.info(f"Scouting financials for {self.ticker}...")
        try:
            # yfinance returns DataFrames. converting to string/dict for LLM consumption
            # We limit to last 3 periods to save tokens
            income_stmt = self.stock.financials.iloc[:, :3].to_string() if not self.stock.financials.empty else "N/A"
            balance_sheet = self.stock.balance_sheet.iloc[:, :3].to_string() if not self.stock.balance_sheet.empty else "N/A"
            cash_flow = self.stock.cashflow.iloc[:, :3].to_string() if not self.stock.cashflow.empty else "N/A"
            
            return {
                "income_statement": income_stmt,
                "balance_sheet": balance_sheet,
                "cash_flow": cash_flow
            }
        except Exception as e:
            logger.error(f"Error fetching financials: {e}")
            return {"error": str(e)}

    def get_news(self) -> list:
        """Fetches recent news."""
        logger.info(f"Scouting news for {self.ticker}...")
        try:
            news = self.stock.news
            # Clean up the news list
            formatted_news = []
            for item in news[:5]: # Top 5 news items
                # Handle nested structure if present (yfinance often nests in 'content')
                content = item.get('content', item)
                
                # Title
                title = content.get('title', 'N/A')
                
                # Publisher
                provider = content.get('provider', {})
                publisher = provider.get('displayName', 'Unknown') if isinstance(provider, dict) else str(provider)
                
                # Link
                click_through = content.get('clickThroughUrl', {})
                link = click_through.get('url', 'N/A') if isinstance(click_through, dict) else str(click_through)
                if link == 'N/A':
                     link = content.get('link', 'N/A')

                # Date
                pub_date = content.get('pubDate', 'N/A')
                # If pubDate is N/A, try providerPublishTime (unix timestamp)
                if pub_date == 'N/A' and 'providerPublishTime' in content:
                    pub_date = datetime.fromtimestamp(content['providerPublishTime']).strftime('%Y-%m-%d')
                
                formatted_news.append({
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "publish_time": pub_date
                })
            return formatted_news
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

    def identify_peers(self, sector: str = "N/A", industry: str = "N/A") -> list:
        """Identifies a pool of potential competitors using reasoning and web search."""
        logger.info(f"Identifying peers for {self.ticker}...")
        company_name = self.stock.info.get('longName') or self.ticker
        try:
            prompt = (
                f"I need to find the top 5 direct public competitors for {company_name} ({self.ticker}). "
                f"Sector: {sector}, Industry: {industry}. "
                f"\n\nCRITICAL INSTRUCTIONS:\n"
                f"1. Use web search to verify who the actual business competitors are. "
                f"2. For each competitor, find their PRIMARY Yahoo Finance ticker symbol. "
                f"3. Strictly use primary listings (e.g., 'BN.PA' for Danone, 'SPOT' for Spotify, 'OR.PA' for L'Oreal). "
                f"4. Exclude {company_name} itself and all its ADRs or secondary listings. "
                f"\nReturn ONLY a comma-separated list of the 5 ticker symbols. No extra text."
            )
            response = query_llm(
                system_prompt="You are a senior equity research analyst. Use web search to identify accurate primary-listing tickers for direct competitors.",
                user_prompt=prompt,
                model="grok-4-1-fast-reasoning",
                tools=[web_search()]
            )
            
            # Extract tickers using regex to handle any potential conversational filler
            # Matches words that might have dots or hyphens (typical of tickers)
            found = re.findall(r'([A-Z0-9^.-]+)', response)
            peers = [t.strip().upper() for t in found if t.strip()]
            
            # Deduplicate while preserving order
            seen = set()
            unique_peers = [p for p in peers if not (p in seen or seen.add(p))]
            
            return unique_peers[:6] # Return up to 6 candidates for filtering
        except Exception as e:
            logger.error(f"Error identifying peers: {e}")
            return []

    def get_peer_data(self, sector: str = "N/A", industry: str = "N/A") -> dict:
        """Fetches key metrics for competitors and filters for the best industry matches."""
        candidates = self.identify_peers(sector, industry)
        peer_data = {}
        
        for peer in candidates:
            if len(peer_data) >= 3:
                break
                
            logger.info(f"Scouting peer data for {peer}...")
            try:
                p_stock = yf.Ticker(peer)
                info = p_stock.info
                
                # 1. Basic Validity Check
                price = info.get('currentPrice') or info.get('regularMarketPrice')
                if not price:
                    logger.warning(f"Peer {peer} has no price data, skipping.")
                    continue

                # 2. Industry/Sector Filtering
                p_sector = info.get('sector', 'N/A')
                p_industry = info.get('industry', 'N/A')
                
                # Check for same company (sometimes LLM fails to filter)
                target_name = self.stock.info.get('longName')
                peer_name = info.get('longName')
                if peer_name and target_name and peer_name == target_name:
                    logger.warning(f"Peer {peer} is actually the same company ({peer_name}). Skipping.")
                    continue

                # Be somewhat flexible but avoid completely unrelated sectors
                # If we have a sector match, it's a strong candidate
                if sector != "N/A" and p_sector != "N/A" and sector != p_sector:
                    # Special handling for conglomerates or very close sectors might go here
                    # For now, we skip to avoid outliers like UMG vs Sixt
                    logger.warning(f"Peer {peer} sector '{p_sector}' mismatch with '{sector}'. Skipping.")
                    continue

                peer_data[peer] = {
                    "price": price,
                    "market_cap": info.get('marketCap', 'N/A'),
                    "pe_ratio": info.get('trailingPE', 'N/A'),
                    "fwd_pe": info.get('forwardPE', 'N/A'),
                    "revenue_growth": info.get('revenueGrowth', 'N/A'),
                    "profit_margins": info.get('profitMargins', 'N/A'),
                    "company_name": info.get('longName') or peer
                }
            except Exception as e:
                logger.warning(f"Failed to fetch data for peer {peer}: {e}")
        
        return peer_data

    def gather_all(self) -> dict:
        """Coordinates the data gathering."""
        market_data = self.get_market_data()
        
        # If we can't get basic market data, don't bother with the rest
        if "error" in market_data:
            return {
                "market_data": market_data,
                "financials": {},
                "news": [],
                "peer_data": {}
            }

        return {
            "market_data": market_data,
            "financials": self.get_financials(),
            "news": self.get_news(),
            "peer_data": self.get_peer_data(market_data.get('sector'), market_data.get('industry'))
        }
