import html
import time
from threading import Lock
from typing import Any

import uvicorn
import yfinance as yf
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from .funds import fund_by_ticker, search_funds

app = FastAPI(title="Index Fund Search", description="Search a curated catalog of index funds.")
QUOTE_CACHE_TTL_SECONDS = 300
_quote_cache: dict[str, tuple[float, dict[str, Any] | None]] = {}
_quote_cache_lock = Lock()


def _fetch_quote(ticker: str) -> dict[str, Any] | None:
    fund = yf.Ticker(ticker)
    try:
        info = fund.info
    except Exception:
        return None

    price = next(
        (
            info.get(key)
            for key in ("regularMarketPrice", "navPrice", "currentPrice", "previousClose")
            if isinstance(info.get(key), (int, float))
        ),
        None,
    )
    if price is None:
        try:
            history = fund.history(period="5d")
            closes = history["Close"].dropna()
            if not closes.empty:
                price = float(closes.iloc[-1])
        except Exception:
            pass

    if price is None:
        return None
    return {
        "price": float(price),
        "currency": info.get("currency"),
        "market_state": info.get("marketState"),
    }


def _cached_quote(ticker: str) -> dict[str, Any] | None:
    now = time.monotonic()
    with _quote_cache_lock:
        cached = _quote_cache.get(ticker)
        if cached is not None and cached[0] > now:
            return cached[1]

    quote = _fetch_quote(ticker)
    with _quote_cache_lock:
        _quote_cache[ticker] = (now + QUOTE_CACHE_TTL_SECONDS, quote)
    return quote


@app.get("/funds")
def get_funds(q: str = Query(default="", description="Search ticker, fund name, or tracked index")):
    return search_funds(q)


@app.get("/funds/{ticker}")
def get_fund(ticker: str):
    fund = fund_by_ticker(ticker)
    if fund is None:
        raise HTTPException(status_code=404, detail="Fund not found")

    result = fund.__dict__.copy()
    result["quote"] = _cached_quote(fund.ticker)
    return result


@app.get("/", response_class=HTMLResponse)
def index(q: str = Query(default="")) -> HTMLResponse:
    escaped_query = html.escape(q, quote=True)
    results = search_funds(q)
    rows = "".join(
        "<tr>"
        f'<td><a href="/funds/{fund["ticker"]}">{html.escape(str(fund["ticker"]))}</a></td>'
        f'<td>{html.escape(str(fund["name"]))}</td>'
        f'<td>{html.escape(str(fund["index"]))}</td>'
        f'<td>{html.escape(str(fund["issuer"]))}</td>'
        "</tr>"
        for fund in results
    )
    if not rows:
        rows = '<tr><td colspan="4">No matching funds found.</td></tr>'

    return HTMLResponse(
        "<!doctype html>"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Index Fund Search</title>"
        "<style>body{font:16px sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem}"
        "input{padding:.55rem;width:min(24rem,70%)}button{padding:.6rem}"
        "table{border-collapse:collapse;width:100%;margin-top:1.5rem}"
        "th,td{text-align:left;border-bottom:1px solid #ddd;padding:.6rem}</style>"
        "</head><body><h1>Index Fund Search</h1>"
        '<form method="get" action="/">'
        f'<input name="q" value="{escaped_query}" placeholder="Ticker, fund name, or index">'
        '<button type="submit">Search</button></form>'
        "<table><thead><tr><th>Ticker</th><th>Fund</th><th>Index</th><th>Issuer</th>"
        f"</tr></thead><tbody>{rows}</tbody></table></body></html>"
    )


def run() -> None:
    uvicorn.run("ml_snp500.web:app", host="127.0.0.1", port=8000)