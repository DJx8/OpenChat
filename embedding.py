import json
import urllib.request
import urllib.error

from google import genai
from google.genai import types

from config import (
    EMBEDDING_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_TIMEOUT,
    OLLAMA_EMBEDDING_MODEL,
    GEMINI_EMBEDDING_MODEL,
    GEMINI_API_KEY,
)


def generate_embeddings(texts, task_type="RETRIEVAL_DOCUMENT"):

    if isinstance(texts, str):
        texts = [texts]

    if not texts:
        return []

    # =================================
    # LOCAL EMBEDDINGS - OLLAMA
    # =================================

    if EMBEDDING_PROVIDER == "ollama":

        data = {"model": OLLAMA_EMBEDDING_MODEL, "input": texts}

        json_data = json.dumps(data).encode("utf-8")

        request = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/embed",
            data=json_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT) as response:

                result = json.loads(response.read().decode("utf-8"))

                return result["embeddings"]

        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama embedding API error: {details}") from error

        except urllib.error.URLError as error:
            raise RuntimeError(
                f"Could not connect to Ollama: {error.reason}"
            ) from error

    # =================================
    # ONLINE EMBEDDINGS - GEMINI
    # =================================

    elif EMBEDDING_PROVIDER == "gemini":

        if not GEMINI_API_KEY:
            raise RuntimeError("Gemini API key is missing.")

        try:
            client = genai.Client(api_key=GEMINI_API_KEY)

            result = client.models.embed_content(
                model=GEMINI_EMBEDDING_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type, output_dimensionality=768
                ),
            )

            return [embedding.values for embedding in result.embeddings]

        except Exception as error:
            raise RuntimeError(f"Gemini embedding API error: {error}") from error

    else:
        raise ValueError(f"Unsupported embedding provider: {EMBEDDING_PROVIDER}")
