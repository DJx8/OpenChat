# 💬 OpenChat

**An AI-powered chatbot with local and cloud LLM support, document-based question answering, and persistent conversation history.**

<p align="center">
  <a href="https://openchat-dj.streamlit.app/">Live Demo</a> ·
  <a href="https://github.com/DJx8/OpenChat">GitHub Repository</a>
</p>

## 🚀 Overview

OpenChat is a ChatGPT-style AI chatbot built using Python and Streamlit. It supports both locally running language models through Ollama and cloud-based models through Google Gemini.

It also includes Retrieval-Augmented Generation (RAG), allowing users to upload PDF or TXT documents and ask questions based on their contents.

## ✨ Features

- **Dual AI providers:** Switch between local Ollama and online Google Gemini.
- **Document Q&A:** Upload PDF and TXT files and ask questions about their contents.
- **RAG pipeline:** Extract, chunk, embed and retrieve relevant document content.
- **Conversation management:** Create, rename, delete and switch between conversations.
- **Persistent storage:** Store conversation history using SQLite.
- **Session isolation:** Separate conversations between browser sessions.
- **Streaming responses:** Display AI-generated responses as they are produced.
- **Usage tracking:** Monitor Gemini requests and token usage during a session.

## 🧠 AI Models

| Provider | Model | Purpose |
|---|---|---|
| Ollama | Qwen 2.5 0.5B | Local chat |
| Google Gemini | Gemini 3.5 Flash-Lite | Online chat |
| Ollama | all-minilm | Local embeddings |
| Google Gemini | gemini-embedding-001 | Online embeddings |

The cloud deployment uses Gemini because it cannot access Ollama running on a user's personal computer.

## 🏗️ Project Architecture

| File | Responsibility |
|---|---|
| `app.py` | Streamlit frontend and application flow |
| `config.py` | Application and model configuration |
| `llm_provider.py` | Local and online LLM integration |
| `embedding.py` | Text embedding generation |
| `similarity.py` | Semantic and keyword-based retrieval |
| `document_processor.py` | PDF/TXT extraction and text chunking |
| `database.py` | SQLite conversation storage |
| `ollama_client.py` | Ollama client utilities |
| `chat_loop.py` | Chat loop utilities |

## 🔍 How RAG Works

OpenChat uses a Retrieval-Augmented Generation pipeline for document-based questions.

1. **Upload:** The user uploads a PDF or TXT file.
2. **Extraction:** Text is extracted from the uploaded document.
3. **Chunking:** The extracted text is split into smaller overlapping chunks.
4. **Embedding:** Each chunk is converted into a numerical vector.
5. **Retrieval:** Relevant chunks are identified using semantic similarity and keyword matching.
6. **Generation:** Retrieved content is passed to the selected LLM to generate an answer.

## 🛠️ Technology Stack

- **Language:** Python
- **Frontend:** Streamlit
- **LLM Integration:** Google Gemini API, Ollama
- **Embeddings:** Gemini Embedding, all-minilm
- **RAG:** Custom retrieval pipeline, cosine similarity and keyword matching
- **Document Processing:** PyMuPDF
- **Database:** SQLite
- **Deployment:** Streamlit Community Cloud
- **Version Control:** Git and GitHub

## 💻 Run Locally

### Prerequisites

- Python 3.13 or a compatible version
- Git
- Ollama (for local model support)
- Google Gemini API key (for online model support)

### 1. Clone the repository

```bash
git clone https://github.com/DJx8/OpenChat.git
cd OpenChat
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Ollama

Install Ollama and download the required models:

```bash
ollama pull qwen2.5:0.5b
ollama pull all-minilm
```

Make sure the Ollama service is running.

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
APP_ENV=local
GEMINI_API_KEY=your_gemini_api_key
EMBEDDING_PROVIDER=ollama
```

Replace the API key with your own. Never commit `.env` to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal.

## ☁️ Cloud Deployment

OpenChat is deployed using Streamlit Community Cloud.

**Live application:** https://openchat-dj.streamlit.app/

Configure the following secrets in Streamlit Community Cloud:

```toml
APP_ENV = "cloud"
EMBEDDING_PROVIDER = "gemini"
GEMINI_API_KEY = "your_gemini_api_key"
```

The cloud version uses Gemini for chat and embeddings. Local Ollama support is available when running the application on a machine with Ollama installed.

## 🔐 Configuration and Storage

- Gemini API credentials are stored in environment variables or Streamlit Secrets.
- Conversation history is stored in SQLite.
- Browser sessions use separate conversation ownership IDs.
- Uploaded document content and embeddings are maintained in application session state.

**Note:** Streamlit Community Cloud's local filesystem is not guaranteed to persist across app restarts or redeployments. The cloud deployment does not provide permanent database storage or user-account authentication.

## 📌 Future Improvements

- Hosted database for durable conversation storage.
- User authentication and account management.
- Improved document retrieval and source references.
- Additional LLM provider integrations.

## 👨‍💻 Author

**Dhananjay A V**

- GitHub: [@DJx8](https://github.com/DJx8)
- LinkedIn: [Dhananjay A V](https://linkedin.com/in/dhananjay-av)

---

*Built as a hands-on project to explore Large Language Models, RAG, embeddings, API integration and full-stack AI application development.*
