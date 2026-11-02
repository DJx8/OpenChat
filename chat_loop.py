
import json
import urllib.request
import urllib.error

url = "http://localhost:11434/api/chat"

# Store the conversation
messages = [
    {
        "role": "system",
        "content": "You are OpenChat, a helpful AI assistant. "
                   "Give clear and simple answers."
    }
]

print("=" * 40)
print("       Welcome to OpenChat AI")
print("=" * 40)
print("Type /exit to quit.")
print("Type /reset to start a new conversation.")
print()

while True:

    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "/exit":
        print("OpenChat: Goodbye!")
        break

    if user_input.lower() == "/reset":
        messages = [
            {
                "role": "system",
                "content": "You are OpenChat, a helpful AI assistant. "
                           "Give clear and simple answers."
            }
        ]
        print("OpenChat: Conversation reset!\n")
        continue

    # Add the user's message to history
    messages.append({
        "role": "user",
        "content": user_input
    })

    data = {
        "model": "qwen2.5:0.5b",
        "messages": messages,
        "stream": False
    }

    json_data = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))

        assistant_response = result["message"]["content"]

        # Store the AI response
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })

        print("\nOpenChat:", assistant_response, "\n")

    except urllib.error.URLError as error:
        # Remove the unanswered user message
        messages.pop()
        print("Could not connect to Ollama:", error, "\n")

    except Exception as error:
        messages.pop()
        print("Something went wrong:", error, "\n")
