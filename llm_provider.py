import json
import urllib.request
import urllib.error

from abc import ABC, abstractmethod

from google import genai
from google.genai import types

from config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SYSTEM_PROMPT,
)

# =================================
# BASE PROVIDER INTERFACE
# =================================


class BaseLLMProvider(ABC):

    @abstractmethod
    def generate_stream(self, messages, usage_callback=None):
        """Generate a streaming response."""
        pass


# =================================
# OLLAMA PROVIDER
# =================================


class OllamaProvider(BaseLLMProvider):

    def generate_stream(self, messages, usage_callback=None):

        system_instructions = [SYSTEM_PROMPT]

        for message in messages:

            if message["role"] == "system":
                system_instructions.append(message["content"])

        conversation = [{"role": "system", "content": "\n\n".join(system_instructions)}]

        conversation.extend(
            message for message in messages if message["role"] != "system"
        )

        data = {
            "model": OLLAMA_MODEL,
            "messages": conversation,
            "stream": True,
            "options": {"temperature": 0},
        }

        json_data = json.dumps(data).encode("utf-8")

        request = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/chat",
            data=json_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:

            with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT) as response:

                for line in response:

                    if not line.strip():
                        continue

                    result = json.loads(line.decode("utf-8"))

                    if "error" in result:
                        raise RuntimeError(result["error"])

                    content = result.get("message", {}).get("content", "")

                    if content:
                        yield content

                    if result.get("done", False):
                        break

        except urllib.error.HTTPError as error:

            details = error.read().decode("utf-8", errors="replace")

            raise RuntimeError(f"Ollama API error: {details}") from error

        except urllib.error.URLError as error:

            raise RuntimeError(
                f"Could not connect to Ollama: {error.reason}"
            ) from error


# =================================
# GEMINI PROVIDER
# =================================


class GeminiProvider(BaseLLMProvider):

    def __init__(self):

        if not GEMINI_API_KEY:
            raise RuntimeError(
                "Gemini API key is missing. "
                "Please configure GEMINI_API_KEY in your .env file."
            )

        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate_stream(self, messages, usage_callback=None):

        system_instructions = [SYSTEM_PROMPT]

        conversation = []

        for message in messages:

            role = message["role"]
            content = message["content"]

            if role == "system":

                system_instructions.append(content)

            elif role in ("user", "assistant"):

                gemini_role = "model" if role == "assistant" else "user"

                conversation.append({"role": gemini_role, "parts": [{"text": content}]})

        latest_usage = None

        try:

            stream = self.client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=conversation,
                config=types.GenerateContentConfig(
                    system_instruction="\n\n".join(system_instructions)
                ),
            )

            for chunk in stream:

                content = chunk.text

                if content:
                    yield content

                # Capture usage information from Gemini

                usage = getattr(chunk, "usage_metadata", None)

                if usage:

                    latest_usage = {
                        "input_tokens": (usage.prompt_token_count or 0),
                        "output_tokens": (usage.candidates_token_count or 0),
                        "total_tokens": (usage.total_token_count or 0),
                    }

            # Send usage information after streaming finishes

            if latest_usage and usage_callback:

                usage_callback(latest_usage)

        except Exception as error:

            raise RuntimeError(f"Gemini API error: {error}") from error


# =================================
# PROVIDER FACTORY
# =================================


def get_provider(provider_name=None):

    if provider_name is None:
        provider_name = LLM_PROVIDER

    provider_name = provider_name.lower()

    if provider_name == "ollama":
        return OllamaProvider()

    elif provider_name == "gemini":
        return GeminiProvider()

    raise ValueError(f"Unsupported LLM provider: {provider_name}")


# =================================
# COMMON GENERATION FUNCTION
# =================================


def generate_response_stream(messages, provider_name=None, usage_callback=None):

    provider = get_provider(provider_name)

    yield from provider.generate_stream(messages, usage_callback=usage_callback)
