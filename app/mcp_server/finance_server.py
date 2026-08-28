import os

import yfinance as yf
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier

auth = JWTVerifier(
    public_key=os.environ["MCP_SHARED_SECRET"],  # param name is misleading — this is your shared secret
    algorithm="HS256",
)

mcp = FastMCP("Finance Server", auth=auth)


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
        port=int(os.environ.get("PORT", 8000)),  # Render assigns PORT dynamically
    )