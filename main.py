import os
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user, system
from xai_sdk.search import SearchParameters
from datetime import datetime
from prompt import generate_prompt
load_dotenv()

today = datetime.now().strftime("%Y-%m-%d")
ticker = input(
    "Enter a stock ticker symbol (e.g., AAPL) or company name: ").upper()
prompt = generate_prompt(ticker)
client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600,  # Override default timeout with longer timeout for reasoning models
)
chat = client.chat.create(
    model="grok-4-1-fast-reasoning", search_parameters=SearchParameters(mode="auto", max_search_results=10))
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
