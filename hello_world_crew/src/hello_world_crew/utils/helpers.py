# Import necessary modules
from dotenv import load_dotenv
import os

from crewai import LLM


# Load environment variables from .env file
load_dotenv()

llm_openai_4m = LLM(
    model=os.getenv("OPENAI_MODEL"),
    temperature=0.0,
    api_key=os.getenv("OPENAI_API_KEY"),
)

llm_deepseek_v3 = LLM(
    model=os.getenv("DEEPSEEK_MODEL"),
    temperature=0.0,
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

llm_nemo = LLM(
    model=os.getenv("OPTOGPT_MODEL_NEMO"),
    base_url=os.getenv("OPTOGPT_BASE_URL"),
    api_key=os.getenv("OPTOGPT_API_KEY"),
)

llm_deepseek_r1 = LLM(
    model=os.getenv("OPTOGPT_MODEL_R1"),
    base_url=os.getenv("OPTOGPT_BASE_URL"),
    api_key=os.getenv("OPTOGPT_API_KEY"),
)
