import os
import time

import jwt

SECRET = os.environ.get("MCP_SHARED_SECRET")

if not SECRET:
    raise SystemExit(
        "MCP_SHARED_SECRET is not set. Export the same secret you put on Railway:\n"
        '  PowerShell:  $env:MCP_SHARED_SECRET = "<your secret>"\n'
        '  bash:        export MCP_SHARED_SECRET="<your secret>"'
    )

TTL_SECONDS = 90 * 24 * 60 * 60  # 90 days
now = int(time.time())

token = jwt.encode(
    {
        "sub": "streamlit-client",
        "iat": now,
        "exp": now + TTL_SECONDS,
    },
    SECRET,
    algorithm="HS256",
)

print(token)
