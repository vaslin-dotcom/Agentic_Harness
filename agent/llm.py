import time
from langchain_openai import ChatOpenAI
from openai import RateLimitError, InternalServerError, APIConnectionError
from dotenv import load_dotenv
load_dotenv()
import os
from tools.tool_registry import tools

MODEL='openai/gpt-oss-120b'

passive_llm=ChatOpenAI(
        model=MODEL,
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=os.getenv("GROQ_BASE_URL"),
        max_retries=2
)
active_llm=passive_llm.bind_tools(tools)

class LLMError(Exception):
    """Raised when the model call fails for good."""

RETRYABLE = (RateLimitError, InternalServerError, APIConnectionError)

def call_llm(messages, retries=3):
    for attempt in range(retries + 1):
        try:
            response = active_llm.invoke(messages)
            break
        except RETRYABLE as e:
            if attempt == retries:
                raise LLMError(f"LLM unavailable after {retries + 1} attempts: {e}") from e
            time.sleep(2 ** attempt)   # wait 1s, 2s, 4s
        except Exception as e:
            raise LLMError(f"LLM call failed: {e}") from e

    usage = (response.response_metadata or {}).get("token_usage", {})
    return response, usage