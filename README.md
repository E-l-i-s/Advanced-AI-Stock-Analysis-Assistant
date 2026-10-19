# AI Stock Analysis Assistant

An AI-powered stock research assistant. Ask about a ticker in natural language and get live market data, historical price charts, balance sheets, news, and company profiles rendered as generative UI (charts, tables, metric cards, and follow-up buttons) by **Thesys C1**.

## Key Components

1. **Backend Service (`/backend`)**:
   - Built on **FastAPI**, streaming responses over Server-Sent Events (`text/event-stream`) to `POST /api/chat`.
   - **LangChain** agent (`create_agent`) calling the **Thesys C1** model through its OpenAI-compatible endpoint (`https://api.thesys.dev/v1/embed/`). The default model is `c1/google/gemini-3.1-flash-lite-free/v-20260331`; override it with `THESYS_MODEL`.
   - Multi-turn memory per `threadId` via **LangGraph** `InMemorySaver` (kept in process memory, so it resets when the server restarts).
   - Market data from **Yahoo Finance (`yfinance`)**:
     - `get_stock_price`: Latest close, previous close, change, and change percent.
     - `get_historical_stock_price`: OHLCV price history for a `YYYY-MM-DD` date range.
     - `get_balance_sheet`: Balance sheet statements (assets, liabilities, equity) by date.
     - `get_stock_news`: Recent headlines with publisher and link.
     - `get_company_profile`: Name, sector, industry, market cap, P/E ratios, 52-week range, and a business summary.

2. **Frontend Application (`/frontend`)**:
   - Built with **React 19**, **TypeScript**, and **Vite 7**.
   - Uses **`@thesysai/genui-sdk`** (`C1Chat`, `ThemeProvider`) and **`@crayonai/react-ui`**.
   - Dark-themed UI with a row of "Quick Inquiries" chips that insert sample prompts into the chat composer.
   - Vite dev server on port `3000`, proxying `/api` to the backend on port `8888`.

---

## Quick Start

### Step 1: Get a Thesys API Key

1. Sign up at [thesys.dev](https://thesys.dev) and create an API key under **Console → API Keys**.
2. Create `backend/.env` (there is no `.env.example` in the repo):

   ```env
   THESYS_API_KEY=your_thesys_api_key_here
   # Optional: override the default model
   # THESYS_MODEL=c1/google/gemini-3.1-flash-lite-free/v-20260331
   ```

   The backend also accepts `OPENAI_API_KEY` as a fallback. Optional `HOST` and `PORT` variables change the bind address (defaults `0.0.0.0:8888`).

### Step 2: Start the Backend

Requires **Python 3.12+** and [uv](https://docs.astral.sh/uv/).

```bash
cd backend

# Install dependencies from pyproject.toml / uv.lock
uv sync

# Run the server (with auto-reload)
uv run python main.py
```

_The backend runs at `http://localhost:8888`._

### Step 3: Start the Frontend

In a second terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the Vite dev server
npm run dev
```

_The app runs at `http://localhost:3000`._

Other frontend scripts: `npm run build` (type-check and production build to `dist/`), `npm run lint`, and `npm run preview`.

---

## Example Prompts

- **Comparative Analysis**: _"Compare Nvidia (NVDA) and AMD stock price performance and valuation metrics."_
- **Historical Charting**: _"Plot the historical closing stock price of Tesla (TSLA) over the past 6 months."_
- **Fundamental Breakdown**: _"Visualize the latest balance sheet statement of Apple (AAPL)."_
- **Market News**: _"Retrieve the latest market news and analyst headlines for Microsoft (MSFT)."_
- **Company Overview**: _"Give me a company profile, market cap, and valuation overview for Amazon (AMZN)."_

---

## API Endpoints

| Method | Endpoint      | Description                                                        |
| :----- | :------------ | :----------------------------------------------------------------- |
| `GET`  | `/`           | Service status, API-key configured flag, and endpoint list         |
| `GET`  | `/api/health` | Health check: status, API-key configured flag, and model name      |
| `POST` | `/api/chat`   | Chat endpoint that streams the assistant's reply as SSE (used by C1Chat) |

If no API key is configured, `/api/chat` streams a setup message instead of calling the model. If Thesys returns a 429 (no credits for the selected model), the stream explains how to switch to the free model or add credits.

---

## Repository Structure

```
├── backend/
│   ├── main.py            # FastAPI app, financial tools, and LangChain agent
│   ├── pyproject.toml     # Python dependencies & project metadata
│   ├── uv.lock            # Locked Python dependency versions
│   ├── .python-version    # Python version pin
│   └── README.md          # Backend documentation
├── frontend/
│   ├── src/
│   │   ├── App.tsx        # Main component: quick-prompt bar and C1Chat
│   │   ├── App.css        # Dark theme styles and chat layout overrides
│   │   └── main.tsx       # React entry point
│   ├── index.html         # HTML template (fonts, title)
│   ├── vite.config.ts     # Vite config: port 3000 and /api proxy
│   ├── eslint.config.js   # ESLint configuration
│   ├── tsconfig*.json     # TypeScript configuration
│   ├── package.json       # Frontend scripts and dependencies
│   └── README.md          # Frontend documentation
├── .gitignore             # Ignored files (.env, .venv, node_modules, dist)
└── README.md              # Project overview and setup guide
```

---

## Disclaimer

This project is for research and educational purposes. Market data comes from Yahoo Finance via `yfinance` and may be delayed or incomplete. It is not investment advice.
