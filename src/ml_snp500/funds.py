from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Fund:
    ticker: str
    name: str
    index: str
    issuer: str
    expense_ratio: float


FUNDS = (
    Fund("SPY", "SPDR S&P 500 ETF Trust", "S&P 500", "State Street", 0.000945),
    Fund("IVV", "iShares Core S&P 500 ETF", "S&P 500", "BlackRock", 0.0003),
    Fund("VOO", "Vanguard S&P 500 ETF", "S&P 500", "Vanguard", 0.0003),
    Fund("SPLG", "SPDR Portfolio S&P 500 ETF", "S&P 500", "State Street", 0.0002),
    Fund("RSP", "Invesco S&P 500 Equal Weight ETF", "S&P 500 Equal Weight", "Invesco", 0.002),
    Fund("VTI", "Vanguard Total Stock Market ETF", "CRSP US Total Market", "Vanguard", 0.0003),
    Fund("ITOT", "iShares Core S&P Total U.S. Stock Market ETF", "S&P Total Market", "BlackRock", 0.0003),
    Fund("SCHB", "Schwab U.S. Broad Market ETF", "Dow Jones U.S. Broad Stock Market", "Charles Schwab", 0.0003),
    Fund("QQQ", "Invesco QQQ Trust", "Nasdaq-100", "Invesco", 0.002),
    Fund("IWM", "iShares Russell 2000 ETF", "Russell 2000", "BlackRock", 0.0019),
    Fund("DIA", "SPDR Dow Jones Industrial Average ETF Trust", "Dow Jones Industrial Average", "State Street", 0.0016),
    Fund("VEA", "Vanguard FTSE Developed Markets ETF", "FTSE Developed All Cap ex US", "Vanguard", 0.0003),
    Fund("IEFA", "iShares Core MSCI EAFE ETF", "MSCI EAFE IMI", "BlackRock", 0.0007),
    Fund("EFA", "iShares MSCI EAFE ETF", "MSCI EAFE", "BlackRock", 0.0032),
    Fund("VWO", "Vanguard FTSE Emerging Markets ETF", "FTSE Emerging Markets All Cap", "Vanguard", 0.0007),
    Fund("EEM", "iShares MSCI Emerging Markets ETF", "MSCI Emerging Markets", "BlackRock", 0.0069),
    Fund("AGG", "iShares Core U.S. Aggregate Bond ETF", "Bloomberg U.S. Aggregate Bond", "BlackRock", 0.0003),
    Fund("BND", "Vanguard Total Bond Market ETF", "Bloomberg U.S. Aggregate Float Adjusted", "Vanguard", 0.0003),
    Fund("TLT", "iShares 20+ Year Treasury Bond ETF", "ICE U.S. Treasury 20+ Year", "BlackRock", 0.0015),
    Fund("SCHD", "Schwab U.S. Dividend Equity ETF", "Dow Jones U.S. Dividend 100", "Charles Schwab", 0.0006),
    Fund("PFRX", "Putnam Focused U.S. Research ETF", "U.S. Large Blend", "Putnam", 0.0035),
)


def fund_by_ticker(ticker: str) -> Fund | None:
    normalized_ticker = ticker.strip().upper()
    return next((fund for fund in FUNDS if fund.ticker == normalized_ticker), None)


def search_funds(query: str = "") -> list[dict[str, str | float]]:
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return [asdict(fund) for fund in FUNDS]

    matches = [
        fund
        for fund in FUNDS
        if any(
            normalized_query in value.casefold()
            for value in (fund.ticker, fund.name, fund.index)
        )
    ]
    matches.sort(key=lambda fund: not fund.ticker.casefold().startswith(normalized_query))
    return [asdict(fund) for fund in matches]