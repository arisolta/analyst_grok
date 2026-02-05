import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from xai_sdk import Client
from xai_sdk.chat import user, system

logger = logging.getLogger(__name__)

def get_client():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY not found in environment variables.")
    return Client(api_key=api_key, timeout=3600) # Long timeout for reasoning

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def query_llm(system_prompt: str, user_prompt: str, model: str = "grok-4-1-fast-reasoning", tools: list = None) -> str:
    """
    Generic function to query the LLM with retry logic.
    """
    logger.info(f"Querying LLM ({model})...")
    client = get_client()
    
    chat = client.chat.create(
        model=model,
        tools=tools
    )
    
    chat.append(system(system_prompt))
    chat.append(user(user_prompt))
    
    response = chat.sample()
    return response.content
