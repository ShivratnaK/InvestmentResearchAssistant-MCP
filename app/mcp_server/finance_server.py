import yfinance as yf
from fastmcp import FastMCP

mcp = FastMCP("Finance Server")


@mcp.tool
def get_stock_price(symbol: str) -> float:
    """Get the current stock price for a stock symbol."""
    ticker = yf.Ticker(symbol.upper())
    price = ticker.fast_info.last_price
    return float(price)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
    )