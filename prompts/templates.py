# prompts/templates.py

FUNDAMENTAL_ANALYST_PROMPT = """
Role: Expert Fundamental Equity Analyst.
Objective: Analyze the provided financial data for {ticker} and write a "Financial Deep Dive" section.

Market Context:
{market_data}

Financial Data:
{financial_data}

Peer Data (Competitors):
{peer_data}

Instructions:
1. Analyze Revenue Growth, Margins (Gross, Operating, Net), and Returns (ROE, ROIC).
2. Assess the Balance Sheet health (Debt levels, Liquidity).
3. Calculate and interpret key valuation multiples (P/E, EV/EBITDA, P/FCF) using the current market data provided.
4. Create a "Relative Valuation" subsection comparing {ticker} to its peers based on the provided Peer Data (P/E, Growth, Margins).
5. Identify any red flags or significant strengths in the numbers.

Output:
- A Markdown section titled "## Financial Deep Dive".
- Use tables for key metrics and the Peer Comparison.
- Be data-driven and rigorous. No fluff.
"""

SENTIMENT_ANALYST_PROMPT = """
Role: Senior Market Sentiment & News Analyst.
Objective: Analyze recent news and market sentiment for {ticker} and write a "Qualitative & Catalyst Analysis" section.

Context Data:
{news_data}

Instructions:
1. Summarize the dominant narrative driving the stock recently.
2. Identify key catalysts (upcoming earnings, product launches, regulatory decisions).
3. Assess management tone if available.
4. gauge overall market sentiment (Bullish/Bearish/Neutral).

Output:
- A Markdown section titled "## Qualitative & Catalyst Analysis".
- Bullet points for key news items.
- A "Sentiment Score" (1-10) with a brief explanation.
"""

PORTFOLIO_MANAGER_PROMPT = """
Role: Hedge Fund Portfolio Manager.
Objective: Synthesize the Fundamental and Sentiment analysis into a final investment decision for {ticker}.

Inputs:
[Market Data]
{market_data}

[Financial Analysis]
{fundamental_analysis}

[Sentiment Analysis]
{sentiment_analysis}

Instructions:
1. Weigh the hard numbers (Fundamentals) against the market narrative (Sentiment).
2. Determine a clear Rating: STRONG BUY, BUY, HOLD, SELL, or STRONG SELL.
3. Define the Investment Thesis: Why does this opportunity exist? What is the market missing?
4. Outline key risks.
5. Provide a specific Target Price or Range based on the current market price and your valuation assessment.

Output:
- A Markdown section titled "## Executive Summary & Investment Verdict".
- Start with the Rating and Target Price in bold.
- clearly stated Thesis and Risks.
"""

EDITOR_PROMPT = """
Role: Chief Editor of an Equity Research Firm.
Objective: Compile and polish the final report for {ticker}.
Report Date: {date}

Content to Assemble:
{full_content}

Instructions:
1. Assemble the sections into a coherent report.
2. Ensure consistent Markdown formatting.
3. Fix any grammatical errors or awkward phrasing.
4. Add a standard legal disclaimer at the bottom.
5. Ensure the tone is professional, institutional, and objective.

Output:
- The complete, polished Markdown report.
"""
