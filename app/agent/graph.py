import asyncio

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


llm = ChatGroq(
    model="qwen/qwen3.6-27b",
    temperature=0
)


async def create_graph():

    # Connect to our Finance MCP Server
    client = MultiServerMCPClient(
        {
            "finance": {
                "transport": "http",
                "url": "https://rubber-emerald-beetle.fastmcp.app/mcp",
            }
        }
    )

    # Get tools exposed by the MCP server
    tools = await client.get_tools()

    # Give the tools to the LLM
    model_with_tools = llm.bind_tools(tools)

    def call_model(state: MessagesState):
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    # Build LangGraph
    builder = StateGraph(MessagesState)

    builder.add_node("llm", call_model)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "llm")

    # If LLM wants a tool → tools
    # Otherwise → finish
    builder.add_conditional_edges(
        "llm",
        tools_condition
    )

    # Tool result goes back to LLM
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