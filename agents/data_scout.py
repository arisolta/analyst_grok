import yfinance as yf
import logging
from datetime import datetime
from agents.utils import query_llm

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

    def identify_peers(self) -> list:
        """Identifies 3 major competitors using LLM."""
        logger.info(f"Identifying peers for {self.ticker}...")
        try:
            prompt = f"Identify the top 3 public competitors for {self.ticker}. Return ONLY the 3 ticker symbols separated by commas (e.g., 'AMD, INTC, QCOM'). Do not add any text."
            response = query_llm(
                system_prompt="You are a financial data assistant.",
                user_prompt=prompt,
                model="grok-4-1-fast-non-reasoning"
            )
            peers = [t.strip().upper() for t in response.split(",") if t.strip()]
            return peers[:3] # Ensure max 3
        except Exception as e:
            logger.error(f"Error identifying peers: {e}")
            return []

    def get_peer_data(self) -> dict:
        """Fetches key metrics for competitors."""
        peers = self.identify_peers()
        peer_data = {}
        
        for peer in peers:
            logger.info(f"Scouting peer data for {peer}...")
            try:
                p_stock = yf.Ticker(peer)
                info = p_stock.info
                peer_data[peer] = {
                    "price": info.get('currentPrice') or info.get('regularMarketPrice', 'N/A'),
                    "market_cap": info.get('marketCap', 'N/A'),
                    "pe_ratio": info.get('trailingPE', 'N/A'),
                    "fwd_pe": info.get('forwardPE', 'N/A'),
                    "revenue_growth": info.get('revenueGrowth', 'N/A'),
                    "profit_margins": info.get('profitMargins', 'N/A')
                }
            except Exception as e:
                logger.warning(f"Failed to fetch data for peer {peer}: {e}")
        
        return peer_data

    def gather_all(self) -> dict:
        """Coordinates the data gathering."""
        return {
            "market_data": self.get_market_data(),
            "financials": self.get_financials(),
            "news": self.get_news(),
            "peer_data": self.get_peer_data()
        }