from fastapi.testclient import TestClient

from ml_snp500 import web

client = TestClient(web.app)


def test_search_returns_ticker_prefix_matches_first():
    response = client.get("/funds", params={"q": "vo"})

    assert response.status_code == 200
    assert response.json()[0]["ticker"] == "VOO"


def test_search_matches_index_case_insensitively():
    response = client.get("/funds", params={"q": "s&p 500"})

    assert response.status_code == 200
    assert {fund["ticker"] for fund in response.json()} >= {"SPY", "IVV", "VOO"}


def test_empty_search_returns_full_catalog():
    response = client.get("/funds")

    assert response.status_code == 200
    assert len(response.json()) == 20


def test_unknown_ticker_returns_404():
    response = client.get("/funds/NOTAFUND")

    assert response.status_code == 404


def test_fund_detail_includes_yfinance_quote(monkeypatch):
    web._quote_cache.clear()
    monkeypatch.setattr(
        web,
        "_fetch_quote",
        lambda ticker: {"price": 500.25, "currency": "USD", "market_state": "REGULAR"},
    )

    response = client.get("/funds/voo")

    assert response.status_code == 200
    assert response.json()["ticker"] == "VOO"
    assert response.json()["quote"]["price"] == 500.25