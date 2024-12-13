from datetime import datetime

import mcp.types as types


def info():
    return types.Tool(
        name="Time",
        description="Retrieve the current server time",
        inputSchema={},
    )


# Fetch current time
async def handler() -> list[types.TextContent]:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [types.TextContent(type="text", text=current_time)]
