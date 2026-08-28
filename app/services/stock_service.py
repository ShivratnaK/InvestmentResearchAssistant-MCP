import yfinance as yf


def get_stock_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    price = ticker.fast_info["last_price"]

    return float(price)

import yfinance as yf


def get_stock_news(symbol: str) -> list:
    """Get recent news for a stock symbol."""

    ticker = yf.Ticker(symbol)
    news = ticker.news

    results = []

    for item in news[:5]:
        content = item.get("content", {})

        results.append({
            "title": content.get("title", ""),
            "summary": content.get("summary", ""),
            "url": content.get("canonicalUrl", {}).get("url", ""),
        })

    return results