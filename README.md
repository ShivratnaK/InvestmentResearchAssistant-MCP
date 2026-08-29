# AI Investment Research Assistant

Streamlit chat UI → LangGraph agent (Groq) → FastMCP finance server over authenticated
streamable HTTP.

| Piece | Path | Host |
| --- | --- | --- |
| MCP server | `app/mcp_server/finance_server.py` | Render (free) |
| Agent | `app/agent/graph.py` | in-process with the UI |
| UI | `app/ui/streamlit_app.py` | Streamlit Community Cloud |

## Environment variables

| Name | Where | Purpose |
| --- | --- | --- |
| `MCP_SHARED_SECRET` | Render | HS256 secret the server verifies bearer tokens against. Use **32+ bytes**. |
| `GROQ_API_KEY` | Streamlit / `.env` | Groq API key for the agent LLM. |
| `MCP_SERVER_URL` | Streamlit / `.env` | Render URL ending in `/mcp` — **no trailing slash**. |
| `MCP_CLIENT_TOKEN` | Streamlit / `.env` | JWT minted from `MCP_SHARED_SECRET`, expires after 90 days. |

Copy `.env.example` to `.env` for local runs.

## Deploy the MCP server to Render

1. Generate a secret (32+ bytes):

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

2. In the Render dashboard choose **New → Blueprint** and pick this repo. `render.yaml`
   declares the service: Docker runtime, free plan, `/healthz` health check, deploy on
   every commit to `main`.
3. Render prompts for `MCP_SHARED_SECRET` during Blueprint creation (`sync: false`, so it
   is never committed). Paste the generated value.
4. Confirm the deploy:

   ```bash
   curl https://<your-service>.onrender.com/healthz
   ```

   Expect `{"status":"ok"}`. An unauthenticated `POST /mcp` must return `401`.

The Dockerfile installs `requirements-server.txt` only, so Streamlit and the agent
stack stay out of the server image — it fits the free plan's 512 MB.

### Free-plan cold starts

Render spins a free web service down after 15 minutes without inbound traffic, and waking
it takes roughly 50 seconds. `langchain-mcp-adapters` defaults to a 30 second timeout, so
`app/agent/graph.py` raises it to 90 to cover the wake-up. Free instance hours are 750 per
workspace per month; spun-down time does not count against them.

## Deploy the UI to Streamlit Community Cloud

1. Mint a client token with the same secret:

   ```bash
   python -m app.make_token
   ```

2. Point the app at `app/ui/streamlit_app.py`.
3. In **Secrets**, set `GROQ_API_KEY`, `MCP_SERVER_URL`, and `MCP_CLIENT_TOKEN`.

Streamlit Cloud installs the root `requirements.txt`.

## Run locally

```bash
uv sync
```

Server (terminal 1):

```bash
python -m app.mcp_server.finance_server
```

UI (terminal 2):

```bash
streamlit run app/ui/streamlit_app.py
```

## Token rotation

`MCP_CLIENT_TOKEN` expires after 90 days. Re-run `python -m app.make_token` and update
the Streamlit secret. To revoke every outstanding token, change `MCP_SHARED_SECRET` on
Render and mint a new one.
