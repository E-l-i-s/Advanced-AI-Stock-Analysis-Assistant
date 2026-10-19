# FinSight AI — Stock Analysis Assistant (Backend)

The backend is a **FastAPI** service that runs a **LangChain** agent. The agent calls **Yahoo Finance (`yfinance`)** tools for market data and streams its replies as Server-Sent Events to the **Thesys C1** generative UI frontend.

---

## 🚀 Key Features

- **Streaming responses**: `POST /api/chat` streams the agent's text tokens as `text/event-stream`.
- **Financial tools** (all in `main.py`):
  - `get_stock_price`: Latest close, previous close, dollar change, and percent change (from the last 5 trading days).
  - `get_historical_stock_price`: Open/High/Low/Close/Volume for a `YYYY-MM-DD` start and end date.
  - `get_balance_sheet`: Balance sheet line items for each reporting date.
  - `get_stock_news`: Up to 6 recent headlines with publisher, link, and publish date.
  - `get_company_profile`: Name, sector, industry, market cap, trailing and forward P/E, 52-week high and low, and a shortened business summary.
- **Conversation memory**: LangGraph `InMemorySaver` keeps history per `threadId`. It lives in process memory and is lost when the server restarts.
- **Error handling**: Tool errors are returned as `error` fields in the tool result instead of crashing the chat. Thesys 429 errors and missing API keys produce a readable message in the stream.

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **FastAPI** (web framework and SSE streaming)
- **Uvicorn** (ASGI server)
- **LangChain** (`create_agent`, `langchain-openai`) and **LangGraph** (checkpointer)
- **Thesys C1** via `https://api.thesys.dev/v1/embed/` (OpenAI-compatible API)
- **yfinance** (market data)
- **python-dotenv** (loads `.env`)
- **Pydantic v2** (request models)

---

## ⚙️ Installation & Setup

### 1. Prerequisites

Install **Python 3.12+** and [uv](https://docs.astral.sh/uv/) (recommended):

```bash
pip install uv
```

### 2. Configure Environment Variables

There is no `.env.example` in the repo. Create `backend/.env` yourself:

```env
THESYS_API_KEY=your_thesys_api_key_here

# Optional
# THESYS_MODEL=c1/google/gemini-3.1-flash-lite-free/v-20260331
# HOST=0.0.0.0
# PORT=8888
```

- Get a free API key at [thesys.dev](https://thesys.dev) → Console → API Keys.
- `OPENAI_API_KEY` is accepted as a fallback for `THESYS_API_KEY`.
- The default model is `c1/google/gemini-3.1-flash-lite-free/v-20260331`. Paid models return HTTP 429 when the Thesys account has no credits.

### 3. Install Dependencies

```bash
uv sync
```

Dependencies are listed in `pyproject.toml` and pinned in `uv.lock`. The project has no build-system table, so use `uv sync` rather than `pip install .`.

### 4. Start the Server

```bash
uv run python main.py
```

The server listens on `http://localhost:8888` and reloads on code changes. The `HOST` and `PORT` variables override the defaults.

---

## 📡 API Endpoints

| Method | Endpoint      | Description                                                                 |
| :----- | :------------ | :-------------------------------------------------------------------------- |
| `GET`  | `/`           | Service name, version, `api_key_configured` flag, and endpoint list         |
| `GET`  | `/api/health` | `status`, `api_key_configured` flag, and the active `model` name            |
| `POST` | `/api/chat`   | Streams the assistant reply as `text/event-stream`                          |

### `POST /api/chat` request body

```json
{
  "prompt": { "content": "Show me Apple's balance sheet", "role": "user" },
  "threadId": "any-unique-thread-id"
}
```

- `prompt.content` (required): the user's message.
- `threadId` (required): reuse the same value to continue a conversation.
- `prompt.id`, `prompt.role`, and `responseId` are optional.

---

## 📁 Files

- `main.py`: app, tools, agent, endpoints, and system prompt.
- `pyproject.toml`: project metadata and dependencies.
- `uv.lock`: locked dependency versions.
- `.python-version`: Python version pin.
