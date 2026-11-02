import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_setting(name, default=None):
    # First check Streamlit Cloud Secrets
    try:
        value = st.secrets.get(name)
        if value is not None:
            return str(value)
    except Exception:
        pass

    # Otherwise check local environment variables
    return os.getenv(name, default)


APP_ENV = get_setting("APP_ENV", "local").lower()

EMBEDDING_PROVIDER = get_setting(
    "EMBEDDING_PROVIDER", "ollama" if APP_ENV == "local" else "gemini"
).lower()

# =================================
# LLM CONFIGURATION
# =================================

# =================================
# EMBEDDING CONFIGURATION
# =================================

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama")

OLLAMA_EMBEDDING_MODEL = "all-minilm"

GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"

# Default provider (will be selected dynamically later)
LLM_PROVIDER = "ollama"


# =================================
# OLLAMA CONFIGURATION
# =================================

OLLAMA_BASE_URL = "http://localhost:11434"

OLLAMA_MODEL = "qwen2.5:0.5b"

OLLAMA_TIMEOUT = 180


# =================================
# GEMINI CONFIGURATION
# =================================

GEMINI_MODEL = "gemini-3.5-flash-lite"

GEMINI_API_KEY = get_setting("GEMINI_API_KEY")


# =================================
# AI SYSTEM INSTRUCTIONS
# =================================


SYSTEM_PROMPT = """
You are OpenChat, a helpful general-purpose AI assistant.

RULES:
1. Answer general questions using your knowledge.
2. Give clear, accurate and relevant answers.
3. Explain technical concepts in simple language when appropriate.
4. Never invent facts, names, dates or achievements.
5. If you do not know something, clearly say so.
6. Do not unnecessarily repeat information.
7. Keep answers focused on the user's question.
"""
