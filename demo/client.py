import asyncio

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


def main():
    try:
        # Run the client logic
        asyncio.run(client_logic())
    finally:
        print("Server terminated.")


async def client_logic():
    async with sse_client(url="http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # List available resources
            resources = await session.list_resources()
            print("Available Resources:", resources, end="\n\n")

            greeting = await session.read_resource("file://greeting.txt/")
            print("Read Resource Greeting:", greeting, end="\n\n")

            # List available tools
            tools = await session.list_tools()
            print("Available Tools:", tools, end="\n\n")
            # result = await session.call_tool("Fetch", {"url": "https://example.com"})
            # print("Tools Call Result:", result, end="\n\n")

            result = await session.call_tool("D1", {"sql":"SELECT name FROM sqlite_master WHERE type='table';","params":[]})
            print("Tools Call Result:", result, end="\n\n")


if __name__ == "__main__":
    main()
