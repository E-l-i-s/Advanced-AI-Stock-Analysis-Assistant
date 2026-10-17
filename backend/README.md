# FinSight AI — Stock Analysis Assistant (Backend)

The **FinSight AI Backend** is an asynchronous API service built with **FastAPI**, **LangChain**, and **Yahoo Finance (yfinance)**. It interfaces with **Thesys Generative UI (C1)** to deliver streaming conversational responses containing real-time charts, financial tables, and interactive UI widgets.

---

## 🚀 Key Features

- **Asynchronous Streaming**: Streams Server-Sent Events (SSE) token-by-token directly to the generative UI frontend.
- **Dynamic Financial Tools**:
  - `get_stock_price`: Fetches real-time price quotes, intraday movements, and previous close.
  - `get_historical_stock_price`: Fetches time-series price data across configurable start/end ranges.
  - `get_balance_sheet`: Extracts balance sheet financial statements (assets, liabilities, shareholder equity) with formatted timestamps.
  - `get_stock_news`: Retrieves the latest company headlines, publishers, and publication timestamps.
  - `get_company_profile`: Retrieves corporate background, sector, industry, PE ratios, market cap, and 52-week ranges.
- **Stateful Thread Management**: Uses LangGraph's `InMemorySaver` checkpointer to maintain conversational context across multiple turns.
- **Resilient Fallbacks**: Sanitized ticker symbol handling and graceful error handling prevent tool exceptions from interrupting chat sessions.

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **FastAPI** (Web framework & SSE streaming)
- **Uvicorn** (ASGI server)
- **LangChain & LangGraph** (Agent orchestration & memory checkpointer)
- **Thesys C1 Model** (`c1/openai/gpt-5/v-20250930` via `https://api.thesys.dev/v1/embed/`)
- **Yahoo Finance (`yfinance`)** (Market data provider)
- **Pydantic v2** (Payload serialization and validation)

---

## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.12+** and **uv** (or standard `pip` / `venv`) installed.

```bash
# If using uv (recommended):
pip install uv
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` to include your free Thesys API key:
```env
THESYS_API_KEY=your_thesys_api_key_here
```
*(Get your free API key at [thesys.dev](https://thesys.dev) -> Console -> API Keys)*

### 3. Install Dependencies
```bash
uv sync
# OR with pip:
# pip install -r pyproject.toml
```

### 4. Start the Backend Server
```bash
uv run python main.py
```
The API server will launch at `http://localhost:8888`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root endpoint displaying service status and available routes |
| `GET` | `/api/health` | Health check endpoint returning backend and API key status |
| `POST` | `/api/chat` | Asynchronous SSE streaming endpoint consumed by Thesys C1 |

---

## 🛡️ License & Submission Notice
Developed for academic/portfolio evaluation as an advanced AI-driven stock intelligence platform.
