# S&P 500 — Machine Learning Predictions

## Index fund search web app

Run the FastAPI application with `uv run ml-snp500-web`, then open
`http://127.0.0.1:8000`. Search the bundled catalog by ticker, fund name, or
tracked index. The JSON API is available at `GET /funds?q=voo` and
`GET /funds/VOO`; fund details include a yfinance quote cached for five minutes.
The catalog is curated and is not a complete list of available funds.

Run the tests with `uv run pytest`.

## Commits:
* Initial commit: initial build completed
* Will be looking into how to improve model performance
* Added a small web app to search a few index funds


**Executive summary**\
ML-SnP500 is an early-stage Python 3.13 project (v0.1.0) that combines S&P 500 next-day direction modeling with a small FastAPI index-fund search app.
Purpose
Predict whether the S&P 500 (^GSPC) will close higher the next day, using Yahoo Finance history, rolling close-ratio and trend features, 
and a Random Forest classifier with walk-forward backtesting. Alongside that, it ships a curated catalog of index ETFs (SPY, VOO, QQQ, bonds, etc.) 
that users can search in the browser or via JSON.
How it is used
* CLI: ``uv run ml-snp500`` trains/evaluates the model, prints holdout and backtest precision, and writes sp500_close.png and predictions.png.
* Web: ``uv run ml-snp500-web`` serves http://127.0.0.1:8000. Search by ticker, name, or index. APIs: GET /funds?q=voo and GET /funds/VOO (quote cached 5 minutes). Catalog is not exhaustive.
* Tests: ``uv run pytest`` (fund search coverage today).
Status
Initial build is in place. The next stated goal is improving model performance. Stack: FastAPI, uvicorn, pandas, scikit-learn, matplotlib, yfinance, managed with uv.