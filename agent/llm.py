import os
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import RateLimitError, InternalServerError, APIConnectionError

from tools.tool_registry import tools

load_dotenv()


class LLMError(Exception):
    """Raised when every provider has failed."""


@dataclass(frozen=True)
class Provider:
    name: str
    model: str
    base_url: str
    key_env: str


# ---- To add a model, add one line here ----
PROVIDERS = [
    Provider("groq-gpt-oss", "openai/gpt-oss-120b",
             os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"), "GROQ_API_KEY"),
    Provider("mistral", "ministral-8b-2512",
             os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1"), "MISTRAL_API_KEY"),
    Provider("groq-llama", "openai/gpt-oss-20b",
             os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"), "GROQ_API_KEY"),
    Provider("gemini-3.1-flash-lite", "gemini-3.1-flash-lite",
             os.getenv("GEMINI_BASE_URL", "https://api.groq.com/openai/v1"), "GEMINI_API_KEY"),

]
# --------------------------------------------


def _build(p: Provider):
    llm = ChatOpenAI(
        model=p.model,
        temperature=0,
        api_key=os.getenv(p.key_env),
        base_url=p.base_url,
        max_retries=0,  # failover is handled below, not inside the SDK
    )
    return llm, llm.bind_tools(tools)


# Skip providers whose key is missing instead of crashing
_ACTIVE = []  # list of (name, passive_llm, active_llm)
for p in PROVIDERS:
    if os.getenv(p.key_env):
        passive, active = _build(p)
        _ACTIVE.append((p.name, passive, active))
    else:
        print(f"[llm] skipping {p.name}: {p.key_env} not set")

if not _ACTIVE:
    raise RuntimeError("No LLM provider configured. Check your .env keys.")

passive_llm = _ACTIVE[0][1]  # kept for existing imports (no failover)
_current = 0                 # index of the provider that worked last


def call_llm(messages, rounds=2):
    """Try the current provider; on any error move to the next, wrapping back to the first.
    If every provider fails in a round, wait briefly and run another round."""
    global _current
    n = len(_ACTIVE)
    last_error = None

    for rnd in range(rounds):
        for i in range(n):
            idx = (_current + i) % n
            name, _, active = _ACTIVE[idx]
            try:
                response = active.invoke(messages)
                _current = idx  # stay on whichever one worked
                usage = (response.response_metadata or {}).get("token_usage", {})
                return response, usage
            except Exception as e:
                last_error = e
                kind = "retryable" if isinstance(e, RETRYABLE) else "error"
                print(f"[llm] {name} failed ({kind}): {e}; trying next")
        if rnd < rounds - 1:
            time.sleep(2 ** rnd)

    raise LLMError(f"All providers failed after {rounds} rounds: {last_error}") from last_error


RETRYABLE = (RateLimitError, InternalServerError, APIConnectionError)

if __name__ == "__main__":
    print(call_llm('HI'))