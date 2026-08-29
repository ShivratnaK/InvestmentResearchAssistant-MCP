FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

# Server-only dependencies — deliberately not the root requirements.txt,
# which also carries Streamlit for the UI deployment.
COPY requirements-server.txt ./
RUN pip install --no-cache-dir -r requirements-server.txt

COPY app ./app

EXPOSE 8000

CMD ["python", "-m", "app.mcp_server.finance_server"]
