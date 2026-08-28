import asyncio
import streamlit as st

import sys
from pathlib import Path

# Ensure project root is available on Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.graph import create_graph


st.set_page_config(
    page_title="AI Investment Research Assistant",
    page_icon="📈",
    layout="centered",
)

st.title("📈 AI Investment Research Assistant")
st.caption("Powered by Groq + LangGraph + MCP")


@st.cache_resource
def get_graph():
    return asyncio.run(create_graph())


graph = get_graph()


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_input = st.chat_input(
    "Ask about a stock or investment concept..."
)


if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner("Researching..."):

            result = asyncio.run(
                graph.ainvoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_input,
                            }
                        ]
                    }
                )
            )

            answer = result["messages"][-1].content

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )