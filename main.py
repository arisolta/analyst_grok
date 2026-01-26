import os
from dotenv import load_dotenv
import yfinance as yf
from xai_sdk import Client
from xai_sdk.chat import user, system
from xai_sdk.tools import web_search
from datetime import datetime
from prompt import generate_prompt
load_dotenv()

today = datetime.now().strftime("%Y-%m-%d")
ticker = input(
    "Enter a stock ticker symbol (e.g., AAPL, SAP.DE, BP.L): ").upper()

# Fetch market data via yfinance
market_data_str = None
try:
    print(f"Fetching real-time data for {ticker} via yfinance...")
    stock = yf.Ticker(ticker)
    info = stock.info
    # Check if we got valid data
    if info and ('regularMarketPrice' in info or 'currentPrice' in info):
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        currency = info.get('currency', 'USD')
        mkt_cap = info.get('marketCap', 'N/A')
        pe_ratio = info.get('trailingPE', 'N/A')
        fwd_pe = info.get('forwardPE', 'N/A')
        company_name = info.get('longName') or info.get(
            'shortName') or ticker

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
        print(f"  > Found: {company_name}")
        print(f"  > Price: {price} {currency}")

    else:
        print("  > Could not retrieve detailed market data (ticker might be invalid or data unavailable).")
except Exception as e:
    print(
        f"  > Warning: yfinance fetch failed ({e}). Proceeding with web-only search.")

prompt = generate_prompt(ticker, market_data=market_data_str)
client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600,  # Override default timeout with longer timeout for reasoning models
)
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[web_search()]
)
chat.append(system(
    "You are Grok, a highly intelligent hedge fund analyst. You're aware that today is " + today + "."))
chat.append(
    user(prompt))
response = chat.sample()
print("REPORT COMPLETED. SAVING TO FILE...")

# Create a new .txt file with datestamp and timestamp filename and write the response
os.makedirs("results", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"results/{ticker}-{timestamp}.txt"
with open(filename, "w") as f:
    f.write(response.content)

print(f"Report saved to {filename}")
