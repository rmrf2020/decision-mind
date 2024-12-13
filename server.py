import logging

import mcp.types as types
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

from tools import router, MODULES

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    app = Server("decision-mind")
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
        if name not in SAMPLE_RESOURCES:
            raise ValueError(f"Unknown resource: {uri}")

        return SAMPLE_RESOURCES[name]

    @app.call_tool()
    async def call_tool(
            name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        try:
            response = await router(name, "handler", arguments)
            return response
        except (ValueError, AttributeError) as e:
            return types.CallToolResult(
                content=types.TextContent(type="text", text=f"Failed to Call Tool {name}: {str(e)}"), isError=True)

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        infos = []
        for module_name, model_info in MODULES.items():
            infos.append(model_info[1])
        return infos

    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        async with sse.connect_sse(
                request.scope, request.receive, request._send
        ) as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )

    async def handle_messages(request):
        return await sse.handle_post_message(request.scope, request.receive, request._send)

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
