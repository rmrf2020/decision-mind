import json
from urllib.parse import urljoin

import aiohttp
import mcp.types as types

from . import alist_client


def info():
    return types.Tool(
        name="Alist Search",
        description="Search files in AList",
        inputSchema={
            "type": "object",
            "required": ["keywords"],
            "properties": {
                "keywords": {
                    "type": "string",
                    "description": "The keywords for searching. This is a required parameter.",
                },
                "parent": {
                    "type": "string",
                    "description": "The directory to search within. Optional, defaults to the root directory.",
                },
                "scope": {
                    "type": "integer",
                    "description": "The type of search. Optional, defaults to 0. 0-All, 1-Folders, 2-Files.",
                },
                "page": {
                    "type": "integer",
                    "description": "The page number for results. Optional, defaults to 1.",
                },
                "per_page": {
                    "type": "integer",
                    "description": "The number of results per page. Optional, defaults to 10.",
                },
                "password": {
                    "type": "string",
                    "description": "The password for accessing protected directories. Optional, defaults to none.",
                }
            },
        },
    )


# Fetch website content
async def handler(
        keywords: str = "",
        parent: str = "/",
        scope: int = 0,
        page: int = 1,
        per_page: int = 10,
        password: str = ""
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    payload = json.dumps({
        "parent": parent,
        "keywords": keywords,
        "scope": scope,
        "page": page,
        "per_page": per_page,
        "password": password
    })
    print("payload", payload)
    url = urljoin(alist_client.endpoint, "/api/fs/search")
    async with aiohttp.ClientSession() as session:
        async with session.request("POST", url, data=payload, headers=alist_client.headers) as response:
            result = await response.json()
            return [types.TextContent(type="text", text=f"{json.dumps(result)}")]
