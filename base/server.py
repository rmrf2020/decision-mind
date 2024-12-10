import logging
import platform
from datetime import datetime
from urllib.parse import urlparse, urlunparse

import httpx
import mcp.types as types
import psutil
import uvicorn
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

logging.basicConfig(level=logging.DEBUG)


# Helper function: Validate and clean up URL
def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    # Reconstruct URL to ensure proper format
    return urlunparse(parsed)


# Fetch website content
async def fetch_website(
        url: str,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    try:
        url = validate_url(url)  # Validate and clean up URL
        headers = {
            "User-Agent": "MCP Test Server (github.com/modelcontextprotocol/python-sdk)"
        }
        async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove all script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text = soup.get_text()

            # Clean up text (remove extra blank lines and spaces)
            lines = (line.strip() for line in text.splitlines())
            text = '\n'.join(line for line in lines if line)

            return [types.TextContent(type="text", text=text)]
    except ValueError as e:
        return [types.TextContent(type="text", text=f"URL validation error: {e}")]
    except httpx.HTTPStatusError as e:
        return [types.TextContent(type="text", text=f"HTTP error: {e.response.status_code} {e.response.reason_phrase}")]


# Fetch current time
async def fetch_time() -> list[types.TextContent]:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [types.TextContent(type="text", text=current_time)]


# Fetch system information
async def get_system_info() -> list[types.TextContent]:
    try:
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        memory = psutil.virtual_memory()
        system_info = platform.uname()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        battery = psutil.sensors_battery()
        battery_info = f"Battery status: {battery.percent}%, {'Charging' if battery.power_plugged else 'On battery'}" if battery else "No battery information"

        info = f"""System Information:
                1. Operating System: {system_info.system} {system_info.release}
                2. Device Name: {system_info.node}
                3. CPU Info:
                   - CPU Core Count: {cpu_count}
                   - CPU Usage: {cpu_percent}
                4. Memory Info:
                   - Total Memory: {memory.total / (1024 ** 3):.2f}GB
                   - Used Memory: {memory.used / (1024 ** 3):.2f}GB
                   - Available Memory: {memory.available / (1024 ** 3):.2f}GB
                   - Usage: {memory.percent}%
                5. Disk Info (Root Directory):
                   - Total Space: {disk.total / (1024 ** 3):.2f}GB
                   - Used Space: {disk.used / (1024 ** 3):.2f}GB
                   - Free Space: {disk.free / (1024 ** 3):.2f}GB
                   - Usage: {disk.percent}%
                6. Network Info:
                   - Sent: {net_io.bytes_sent / (1024 ** 2):.2f}MB
                   - Received: {net_io.bytes_recv / (1024 ** 2):.2f}MB
                7. {battery_info}"""

        return [types.TextContent(type="text", text=info)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Failed to retrieve system info: {str(e)}")]


def main() -> None:
    app = Server("mcp-website-fetcher")

    # Define resource list
    SAMPLE_RESOURCES = {
        "greeting": "Hello! This is a sample text resource.",
        "help": "This server provides a few sample text resources for testing.",
        "about": "This is the MCP demo server implementation.",
    }

    @app.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                uri=f"file://{name}.txt",
                name=name,
                description=f"A sample text resource named {name}",
                mimeType="text/plain",
            )
            for name in SAMPLE_RESOURCES.keys()
        ]

    @app.read_resource()
    async def read_resource(uri: str) -> str | bytes:
        print("Received resource URI:", uri)
        # parsed = urlparse(uri)
        name = str(uri).replace("file://", "").replace(".txt", "").replace("/", "")
        print("Received resource name:", name)
        if name not in SAMPLE_RESOURCES:
            raise ValueError(f"Unknown resource: {uri}")

        return SAMPLE_RESOURCES[name]

    @app.call_tool()
    async def fetch_tool(
            name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name == "Fetch":
            if "url" not in arguments:
                raise ValueError("Missing required parameter 'url'")
            return await fetch_website(arguments["url"])
        elif name == "Time":
            return await fetch_time()  # Call fetch_time method
        elif name == "System Info":
            return await get_system_info()
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="Fetch",
                description="Retrieve website content and return it",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the website to fetch content from",
                        }
                    },
                },
            ),
            types.Tool(
                name="Time",
                description="Retrieve the current server time",
                inputSchema={},
            ),
            types.Tool(
                name="System Info",
                description="Retrieve system information (CPU, memory, disk, etc.)",
                inputSchema={},
            ),
        ]

    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        async with sse.connect_sse(
                request.scope, request.receive, request._send
        ) as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )

    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"])
        ],
    )

    uvicorn.run(starlette_app, host="0.0.0.0", port=8000, log_level="debug")


if __name__ == "__main__":
    main()
