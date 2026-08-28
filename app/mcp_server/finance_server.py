from fastmcp import FastMCP
from app.services.stock_service import get_stock_price as fetch_stock_price

mcp = FastMCP("Finance Server")


@mcp.tool
def get_stock_price(symbol: str) -> float:
    """Get the current stock price for a stock symbol."""
    return fetch_stock_price(symbol)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
    )