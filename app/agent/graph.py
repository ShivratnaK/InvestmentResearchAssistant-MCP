import asyncio
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


def require_env(name: str) -> str:
    """Read a required environment variable, failing with a readable message."""
    value = os.environ.get(name)

    if not value:
        raise RuntimeError(
            f"{name} is not set. Add it to .env locally, or to Secrets on Streamlit Cloud."
        )

    return value


async def create_graph():

    require_env("GROQ_API_KEY")

    llm = ChatGroq(
        model="qwen/qwen3.6-27b",
        temperature=0,
    )

    client = MultiServerMCPClient(
        {
            "finance": {
                "transport": "streamable_http",
                "url": require_env("MCP_SERVER_URL"),  # Render URL, e.g. https://xxx.onrender.com/mcp
                "headers": {
                    "Authorization": f"Bearer {require_env('MCP_CLIENT_TOKEN')}"
                },
                # Render spins a free service down after 15 minutes idle and takes
                # ~50s to wake. The adapter default is 30s, which the first request
                # after an idle period would always exceed.
                "timeout": 90,
            }
        }
    )

    tools = await client.get_tools()

    model_with_tools = llm.bind_tools(tools)

    def call_model(state: MessagesState):
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)

    builder.add_node("llm", call_model)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "llm")

    builder.add_conditional_edges(
        "llm",
        tools_condition,
    )

    builder.add_edge("tools", "llm")

    return builder.compile()


async def main():

    graph = await create_graph()

    print("\nAI Investment Research Assistant")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        result = await graph.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            }
        )

        print("\nAgent:", result["messages"][-1].content)
        print()


if __name__ == "__main__":
    asyncio.run(main())
