import os

import yfinance as yf
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from starlette.requests import Request
from starlette.responses import JSONResponse


def require_env(name: str) -> str:
    """Read a required environment variable, failing with a readable message."""
    value = os.environ.get(name)

    if not value:
        raise RuntimeError(
            f"{name} is not set. Add it under Environment on the Render service."
        )

    return value


auth = JWTVerifier(
    public_key=require_env("MCP_SHARED_SECRET"),  # param name is misleading — this is your shared secret
    algorithm="HS256",
)

mcp = FastMCP("Finance Server", auth=auth)


@mcp.custom_route("/healthz", methods=["GET"])
async def healthz(request: Request) -> JSONResponse:
    """Unauthenticated liveness probe for Render's health check."""
    return JSONResponse({"status": "ok"})


@mcp.tool
def get_stock_price(symbol: str) -> float:
    """Get the current stock price for a stock symbol."""
    ticker = yf.Ticker(symbol.upper())
    price = ticker.fast_info.last_price

    if price is None:
        raise ValueError(f"No price available for symbol {symbol!r}.")

    return float(price)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),  # Render assigns PORT dynamically
    )
