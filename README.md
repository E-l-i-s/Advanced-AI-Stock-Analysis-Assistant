# stock analysis assistant

### Key Components

1. **Backend Service (`/backend`)**:
   - Built on **FastAPI** with Server-Sent Events (`text/event-stream`) streaming.
   - **LangChain** agent powered by Thesys C1 (`c1/openai/gpt-5/v-20250930`).
   - Multi-turn conversation state persistence via **LangGraph** `InMemorySaver`.
   - Real-time financial tools powered by **Yahoo Finance (`yfinance`)**:
     - `get_stock_price`: Live quote, daily change, and previous close.
     - `get_historical_stock_price`: Time-series OHLCV price history across date ranges.
     - `get_balance_sheet`: Fundamental assets, liabilities, and equity statements.
     - `get_stock_news`: Latest market and analyst headlines.
     - `get_company_profile`: Corporate background, market cap, and valuation multiples.

2. **Frontend Application (`/frontend`)**:
   - Built with **React 19**, **TypeScript**, and **Vite**.
   - Integrates **`@thesysai/genui-sdk`** (`C1Chat`, `ThemeProvider`) and **`@crayonai/react-ui`**.
   - Includes real-time backend health status monitoring, prompt suggestion chips, and responsive dark glassmorphic UI.

---

## Quick Start Guide

### Step 1: Clone and Configure Environment

1. Obtain a free API key at [thesys.dev](https://thesys.dev) (Console -> API Keys).
2. Create `backend/.env` based on `backend/.env.example`:
   ```env
   THESYS_API_KEY=your_thesys_api_key_here
   ```

---

### Step 2: Start the Backend

```bash
cd backend

# Install dependencies (using uv or pip)
uv sync

# Run the server
uv run python main.py
```

_The backend starts at `http://localhost:8888`._

---

### Step 3: Start the Frontend

Open a second terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

_The frontend dashboard will be live at `http://localhost:3000`._

---

## 💡 Example Prompt Inquiries

- **Comparative Analysis**: _"Compare Nvidia (NVDA) and AMD in terms of stock performance and valuation metrics."_
- **Historical Charting**: _"Plot the historical closing price of Tesla (TSLA) over the past 6 months."_
- **Fundamental Breakdown**: _"Show me the latest balance sheet statement of Apple (AAPL)."_
- **Market News**: _"What is the latest news and market sentiment for Microsoft (MSFT)?"_
- **Company Overview**: _"Give me a profile, industry breakdown, and P/E ratio for Amazon (AMZN)."_

---

## Repository Structure

```
├── backend/
│   ├── main.py            # FastAPI application & LangChain financial agent
│   ├── pyproject.toml     # Python dependencies & project metadata
│   ├── .env.example       # Example environment variables template
│   └── README.md          # In-depth backend documentation
├── frontend/
│   ├── src/
│   │   ├── App.tsx        # Main application component & header
│   │   ├── App.css        # Custom styling & dark theme tokens
│   │   └── main.tsx       # React entry point
│   ├── index.html         # Document template with modern fonts
│   ├── vite.config.ts     # Vite configuration with API proxy
│   ├── package.json       # Frontend scripts and dependencies
│   └── README.md          # Frontend documentation
└── README.md              # Project overview & submission guide
```
