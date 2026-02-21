import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS = 4096
GROQ_TEMPERATURE = 0.7

# Rate limiting for free tier
MAX_REQUESTS_PER_MINUTE = 20
MAX_TOKENS_PER_MINUTE = 1000000

OUTPUT_DIR = "output"