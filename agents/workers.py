from agents.utils import query_llm
from xai_sdk.tools import web_search
from prompts.templates import (
    FUNDAMENTAL_ANALYST_PROMPT,
    SENTIMENT_ANALYST_PROMPT,
    PORTFOLIO_MANAGER_PROMPT,
    EDITOR_PROMPT
)

class FundamentalAnalyst:
    def __init__(self, ticker):
        self.ticker = ticker

    def run(self, financial_data: dict, market_data: dict, peer_data: dict) -> str:
        # Format the data into a readable string for the prompt
        formatted_financials = f"""
        Income Statement (Recent):
        {financial_data.get('income_statement', 'N/A')}
        
        Balance Sheet (Recent):
        {financial_data.get('balance_sheet', 'N/A')}
        
        Cash Flow (Recent):
        {financial_data.get('cash_flow', 'N/A')}
        """

        formatted_market = f"""
        Current Price: {market_data.get('current_price')} {market_data.get('currency')}
        Market Cap: {market_data.get('market_cap')}
        Trailing P/E: {market_data.get('pe_ratio')}
        Forward P/E: {market_data.get('fwd_pe')}
        """
        
        formatted_peers = ""
        for ticker, data in peer_data.items():
            formatted_peers += f"- {ticker}: P/E={data.get('pe_ratio')}, Fwd P/E={data.get('fwd_pe')}, Margins={data.get('profit_margins')}, Rev Growth={data.get('revenue_growth')}\n"
        
        prompt = FUNDAMENTAL_ANALYST_PROMPT.format(
            ticker=self.ticker,
            market_data=formatted_market,
            financial_data=formatted_financials,
            peer_data=formatted_peers
        )
        
        return query_llm(
            system_prompt="You are an expert Fundamental Equity Analyst.",
            user_prompt=prompt
        )

class SentimentAnalyst:
    def __init__(self, ticker):
        self.ticker = ticker

    def run(self, news_data: list, market_context: dict) -> str:
        # Step 1: Specific search for Management Tone/Guidance
        tone_search_prompt = f"Search for the latest earnings call transcripts, management quotes, and future guidance for {self.ticker}. Summarize the management's tone (Confident/Cautious/Bearish) and key quotes."
        management_context = query_llm(
            system_prompt="You are a researcher. Use the web search tool to find information.",
            user_prompt=tone_search_prompt,
            model="grok-4-1-fast-reasoning", # Use reasoning model to effectively search and synthesize
            tools=[web_search()]
        )

        # Format news
        news_str = ""
        for item in news_data:
            news_str += f"- {item['title']} (Source: {item['publisher']}, Date: {item['publish_time']})\n"
            
        context_str = f"""
        Sector: {market_context.get('sector')}
        Industry: {market_context.get('industry')}
        Beta: {market_context.get('beta')}
        """
        
        # Combine gathered news with the web-searched management context
        combined_data = f"""
        Recent News Headlines:
        {news_str}
        
        Management Tone & Earnings Context (Web Search Results):
        {management_context}
        
        Market Context:
        {context_str}
        """
        
        prompt = SENTIMENT_ANALYST_PROMPT.format(
            ticker=self.ticker,
            news_data=combined_data
        )
        
        return query_llm(
            system_prompt="You are a Senior Market Sentiment Analyst.",
            user_prompt=prompt,
            model="grok-4-1-fast-non-reasoning" 
        )

class PortfolioManager:
    def __init__(self, ticker):
        self.ticker = ticker

    def run(self, fundamental_analysis: str, sentiment_analysis: str, market_data: dict) -> str:
        formatted_market = f"""
        Current Price: {market_data.get('current_price')} {market_data.get('currency')}
        Market Cap: {market_data.get('market_cap')}
        Sector: {market_data.get('sector')}
        """

        prompt = PORTFOLIO_MANAGER_PROMPT.format(
            ticker=self.ticker,
            market_data=formatted_market,
            fundamental_analysis=fundamental_analysis,
            sentiment_analysis=sentiment_analysis
        )
        
        return query_llm(
            system_prompt="You are a Hedge Fund Portfolio Manager.",
            user_prompt=prompt
        )

class Editor:
    def __init__(self, ticker):
        self.ticker = ticker

    def run(self, sections: dict, date_str: str = "N/A") -> str:
        # Combine all sections
        full_content = ""
        for title, content in sections.items():
            full_content += f"\n\n{content}\n"
            
        prompt = EDITOR_PROMPT.format(
            ticker=self.ticker,
            full_content=full_content,
            date=date_str
        )
        
        return query_llm(
            system_prompt="You are the Chief Editor of an Equity Research Firm.",
            user_prompt=prompt,
            model="grok-4-1-fast-non-reasoning" # Fast model for formatting
        )
