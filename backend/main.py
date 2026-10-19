"""
FinSight AI — Intelligent Financial Market & Stock Analysis Assistant
Backend service built with FastAPI, LangChain, and Thesys Generative UI (C1).
"""

import os
import math
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage, AIMessageChunk
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

import yfinance as yf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("finsight-backend")

# Load environment variables explicitly from backend/.env and current directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_file = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path=dotenv_file, override=True)
load_dotenv(override=True)

# Extract API key (supports either THESYS_API_KEY or OPENAI_API_KEY)
API_KEY = os.getenv("THESYS_API_KEY") or os.getenv("OPENAI_API_KEY")

if API_KEY:
    os.environ["OPENAI_API_KEY"] = API_KEY
    logger.info("Thesys/OpenAI API Key successfully loaded from environment.")
else:
    logger.warning(
        "No THESYS_API_KEY or OPENAI_API_KEY detected in backend/.env. "
        "Get a free API key at https://thesys.dev and add it to backend/.env"
    )

# Thesys C1 Embedded LLM model setup
# Default to a free-tier model; override via THESYS_MODEL in backend/.env
# (paid models return 429 "Http Exception" when the Thesys org has no credits)
THESYS_MODEL_NAME = os.getenv("THESYS_MODEL", "c1/google/gemini-3.1-flash-lite-free/v-20260331")
THESYS_BASE_URL = "https://api.thesys.dev/v1/embed/"

model = ChatOpenAI(
    model=THESYS_MODEL_NAME,
    base_url=THESYS_BASE_URL,
    api_key=API_KEY or "unconfigured_placeholder_key"
)

# Persistent conversational memory for multi-turn threads
conversation_checkpointer = InMemorySaver()


# ============================================================================
# Financial Data Tools (Yahoo Finance Integration)
# ============================================================================

@tool("get_stock_price", description="Retrieves the current market price and latest closing quote for a given stock ticker symbol.")
def get_stock_price(ticker: str) -> Dict[str, Any]:
    """Fetch the most recent trading price for a ticker symbol."""
    clean_ticker = ticker.strip().upper()
    logger.info(f"Invoking get_stock_price for ticker: {clean_ticker}")
    try:
        stock = yf.Ticker(clean_ticker)
        history = stock.history(period="5d")
        if history.empty:
            return {"ticker": clean_ticker, "error": f"No market quote data found for symbol '{clean_ticker}'."}
        
        latest_close = float(history["Close"].iloc[-1])
        previous_close = float(history["Close"].iloc[-2]) if len(history) > 1 else latest_close
        price_change = latest_close - previous_close
        change_pct = (price_change / previous_close * 100) if previous_close else 0.0

        return {
            "ticker": clean_ticker,
            "current_price": round(latest_close, 2),
            "previous_close": round(previous_close, 2),
            "change": round(price_change, 2),
            "change_percent": f"{change_pct:+.2f}%",
            "currency": stock.fast_info.get("currency", "USD") if hasattr(stock, "fast_info") else "USD"
        }
    except Exception as exc:
        logger.error(f"Error retrieving stock price for {clean_ticker}: {exc}")
        return {"ticker": clean_ticker, "error": f"Failed to retrieve stock price: {str(exc)}"}


@tool("get_historical_stock_price", description="Retrieves historical closing prices and volume for a ticker symbol across a specified start and end date range (format: YYYY-MM-DD).")
def get_historical_stock_price(ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Fetch historical stock price time-series within the given date boundaries."""
    clean_ticker = ticker.strip().upper()
    logger.info(f"Invoking get_historical_stock_price for {clean_ticker} from {start_date} to {end_date}")
    try:
        stock = yf.Ticker(clean_ticker)
        history = stock.history(start=start_date, end=end_date)
        if history.empty:
            return {"ticker": clean_ticker, "error": f"No historical records found for '{clean_ticker}' between {start_date} and {end_date}."}
        
        # Format index as ISO date strings to ensure reliable JSON serialization
        history.index = history.index.strftime("%Y-%m-%d")
        return {
            "ticker": clean_ticker,
            "data_points": len(history),
            "start_date": start_date,
            "end_date": end_date,
            "prices": history[["Open", "High", "Low", "Close", "Volume"]].round(2).to_dict()
        }
    except Exception as exc:
        logger.error(f"Error retrieving historical data for {clean_ticker}: {exc}")
        return {"ticker": clean_ticker, "error": f"Failed to retrieve historical data: {str(exc)}"}


def _json_safe_number(val: Any) -> Optional[float]:
    """Convert a value to float, mapping missing/NaN values to None (NaN is not valid JSON)."""
    if val is None:
        return None
    try:
        number = float(val)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(number) else number


@tool("get_balance_sheet", description="Retrieves the fundamental balance sheet statement containing assets, liabilities, and equity for a given stock ticker.")
def get_balance_sheet(ticker: str) -> Dict[str, Any]:
    """Fetch balance sheet financial statement data for the requested ticker."""
    clean_ticker = ticker.strip().upper()
    logger.info(f"Invoking get_balance_sheet for ticker: {clean_ticker}")
    try:
        stock = yf.Ticker(clean_ticker)
        bs = stock.balance_sheet
        if bs is None or bs.empty:
            return {"ticker": clean_ticker, "error": f"No balance sheet statement available for '{clean_ticker}'."}
        
        # Convert Timestamp column headers to ISO date strings for clean serialization
        formatted_bs: Dict[str, Any] = {}
        for col in bs.columns:
            date_key = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
            formatted_bs[date_key] = {
                str(metric): _json_safe_number(val)
                for metric, val in bs[col].items()
            }
        return {"ticker": clean_ticker, "balance_sheet": formatted_bs}
    except Exception as exc:
        logger.error(f"Error retrieving balance sheet for {clean_ticker}: {exc}")
        return {"ticker": clean_ticker, "error": f"Failed to retrieve balance sheet: {str(exc)}"}


@tool("get_stock_news", description="Fetches latest market news articles, press releases, and editorial updates for a given ticker symbol.")
def get_stock_news(ticker: str) -> List[Dict[str, Any]]:
    """Retrieve top recent news publications relating to the specified ticker."""
    clean_ticker = ticker.strip().upper()
    logger.info(f"Invoking get_stock_news for ticker: {clean_ticker}")
    try:
        # Ticker.news currently returns an empty list for many tickers in yfinance 0.2.66;
        # yf.Search returns the same headlines, so use it first and fall back to Ticker.news.
        raw_news = yf.Search(clean_ticker, news_count=6).news or yf.Ticker(clean_ticker).news
        if not raw_news:
            return [{"title": f"No recent headlines found for {clean_ticker}", "publisher": "Yahoo Finance"}]
        
        sanitized_articles = []
        for article in raw_news[:6]:
            content = article.get("content", {}) if "content" in article else article
            sanitized_articles.append({
                "title": content.get("title", "Untitled Article"),
                "publisher": content.get("provider", {}).get("displayName", "Financial News") if isinstance(content.get("provider"), dict) else content.get("publisher", "Financial News"),
                "link": content.get("canonicalUrl", {}).get("url", "") if isinstance(content.get("canonicalUrl"), dict) else content.get("link", ""),
                "published": content.get("pubDate", "") or str(content.get("providerPublishTime", ""))
            })
        return sanitized_articles
    except Exception as exc:
        logger.error(f"Error retrieving news for {clean_ticker}: {exc}")
        return [{"error": f"Failed to retrieve news feed: {str(exc)}"}]


@tool("get_company_profile", description="Retrieves corporate fundamentals including sector, industry, market cap, PE ratio, 52-week price range, and business summary for a ticker.")
def get_company_profile(ticker: str) -> Dict[str, Any]:
    """Retrieve company profile and fundamental valuation metrics."""
    clean_ticker = ticker.strip().upper()
    logger.info(f"Invoking get_company_profile for ticker: {clean_ticker}")
    try:
        stock = yf.Ticker(clean_ticker)
        info = stock.info or {}
        return {
            "symbol": clean_ticker,
            "name": info.get("shortName") or info.get("longName", clean_ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap"),
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "summary": (info.get("longBusinessSummary") or "No overview available.")[:350] + "..."
        }
    except Exception as exc:
        logger.error(f"Error retrieving company profile for {clean_ticker}: {exc}")
        return {"symbol": clean_ticker, "error": f"Failed to retrieve profile: {str(exc)}"}


# Assemble tools and create agent
tools = [
    get_stock_price,
    get_historical_stock_price,
    get_balance_sheet,
    get_stock_news,
    get_company_profile
]

financial_agent = create_agent(
    model=model,
    checkpointer=conversation_checkpointer,
    tools=tools
)

# ============================================================================
# FastAPI App & Schema Definition
# ============================================================================

app = FastAPI(
    title="FinSight AI Stock Analysis Assistant API",
    version="1.0.0",
    description="Intelligent financial market analysis with interactive Generative UI powered by LangChain and Thesys C1."
)

# Configure CORS for local development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptObject(BaseModel):
    content: str = Field(..., description="The message content provided by the user.")
    id: Optional[str] = Field(None, description="Unique prompt message ID.")
    role: Optional[str] = Field("user", description="Message role (user/assistant).")


class RequestObject(BaseModel):
    prompt: PromptObject = Field(..., description="User prompt payload.")
    threadId: str = Field(..., description="Unique conversational thread identifier.")
    responseId: Optional[str] = Field(None, description="Response tracking identifier.")


# ============================================================================
# API Endpoints
# ============================================================================

def get_api_key() -> Optional[str]:
    """Dynamically fetch current API key from environment."""
    return os.getenv("THESYS_API_KEY") or os.getenv("OPENAI_API_KEY") or API_KEY


@app.get("/")
async def root():
    """Service status and endpoint directory."""
    return {
        "service": "FinSight AI Stock Analysis Assistant",
        "status": "online",
        "version": "1.0.0",
        "api_key_configured": bool(get_api_key()),
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat (POST)"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health status and configuration verification."""
    return {
        "status": "healthy",
        "api_key_configured": bool(get_api_key()),
        "model": THESYS_MODEL_NAME
    }


SYSTEM_PROMPT = (
    "You are FinSight AI, an elite financial research and stock market analysis assistant. "
    "You provide institutional-grade stock intelligence, financial visualizations, comparative valuations, "
    "and corporate health breakdowns. "
    "You have real-time access to Yahoo Finance tools for: "
    "1) live quotes and intraday price changes, "
    "2) historical price trends across customizable date ranges, "
    "3) fundamental balance sheet statements, "
    "4) recent corporate press releases and market news, "
    "5) corporate profile and valuation ratios. "
    "Always take advantage of dynamic generative UI capabilities to display informative charts, metric cards, "
    "comparative tables, and interactive follow-up buttons for deeper exploration whenever relevant."
)


@app.post("/api/chat")
async def chat(request: RequestObject):
    """
    Primary chat completion endpoint supporting server-sent events (SSE) streaming.
    Streams generative UI tokens directly to the Thesys C1 frontend component.
    """
    active_key = get_api_key()
    # Verify API key configuration
    if not active_key:
        def key_warning_stream():
            warning_msg = (
                "⚠️ **Thesys API Key Required**\n\n"
                "Please configure your `THESYS_API_KEY` in `backend/.env`.\n\n"
                "1. Sign up for free at [thesys.dev](https://thesys.dev)\n"
                "2. Generate an API Key under Console -> API Keys\n"
                "3. Add `THESYS_API_KEY=your_key_here` to `backend/.env`\n"
                "4. Restart the backend server."
            )
            yield warning_msg

        return StreamingResponse(
            key_warning_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive"
            }
        )

    execution_config = {"configurable": {"thread_id": request.threadId}}

    def stream_generator():
        try:
            for token, _ in financial_agent.stream(
                {
                    "messages": [
                        SystemMessage(SYSTEM_PROMPT),
                        HumanMessage(request.prompt.content)
                    ]
                },
                stream_mode="messages",
                config=execution_config
            ):
                # Only stream assistant-generated content. ToolMessage chunks
                # carry raw tool output (JSON/dicts) and must never be streamed
                # to the C1 Generative UI renderer.
                if not isinstance(token, AIMessageChunk):
                    continue
                if token.content:
                    yield token.content
        except Exception as err:
            err_str = str(err)
            err_body = getattr(err, "body", None)
            logger.error(
                f"Streaming generation error from Thesys API: "
                f"type={type(err).__name__} message={err_str!r} body={err_body!r}"
            )
            if "Http Exception" in err_str or "429" in err_str or "balance" in err_str.lower():
                user_friendly_msg = (
                    "\n\n⚠️ **Thesys API Notice: Insufficient Balance / Rate Limit (HTTP 429)**\n\n"
                    "Thesys returned: *\"Http Exception\" (code 429)* — the organization has no credits for paid models.\n\n"
                    "**How to fix (either option):**\n"
                    "1. Free: set `THESYS_MODEL=c1/google/gemini-3.1-flash-lite-free/v-20260331` in `backend/.env` and restart the backend\n"
                    "2. Paid: visit the [Thesys Console](https://console.thesys.dev/) and add credits under **Billing / Usage**"
                )
                yield user_friendly_msg
            else:
                yield f"\n\n*Error during financial analysis: {err_str}*"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive"
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8888))
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(f"Starting FinSight AI backend server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)