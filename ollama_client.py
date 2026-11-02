
import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:0.5b"

SYSTEM_PROMPT = (
    "You are OpenChat, a helpful general-purpose AI assistant. "
    "Give clear, useful and easy-to-understand answers."
)


def generate_response_stream(messages):

    conversation = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ] + messages

    data = {
        "model": MODEL,
        "messages": conversation,
        "stream": True
    }

    json_data = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:

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
        details = error.read().decode(
            "utf-8", errors="replace"
        )
        raise RuntimeError(
            f"Ollama API error: {details}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Could not connect to Ollama: {error.reason}"
        ) from error
