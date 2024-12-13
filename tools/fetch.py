from urllib.parse import urlparse, urlunparse

import httpx
import mcp.types as types
from bs4 import BeautifulSoup


def info():
    return types.Tool(
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
    )


# Fetch website content
async def handler(
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


# Helper function: Validate and clean up URL
def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    # Reconstruct URL to ensure proper format
    return urlunparse(parsed)
