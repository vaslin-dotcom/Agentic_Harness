import time
from langchain_openai import ChatOpenAI
from openai import RateLimitError, InternalServerError
from dotenv import load_dotenv
load_dotenv()
import os
from tools import tools

MODEL='openai/gpt-oss-120b'

passive_llm=ChatOpenAI(
        model=MODEL,
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=os.getenv("GROQ_BASE_URL"),
        max_retries=2
)
active_llm=passive_llm.bind_tools(tools)

def call_llm(message):
    response = active_llm.invoke(message)
    return response,response.response_metadata['token_usage']
if '__main__' == __name__:
    pass