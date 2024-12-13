import json
import os

import mcp.types as types
import requests


def info():
    return types.Tool(
        name="D1",
        description="Execute SQL in the CloudFlare D1 database",
        inputSchema={
            "type": "object",
            "required": ["sql", "params"],
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "The SQL query to execute. This should be a valid SQL string.",
                },
                "params": {
                    "type": "list",
                    "description": " list of parameters to be bound to the SQL query. Use this to pass dynamic values safely and prevent SQL injection.",
                }
            },
        },
    )


# Fetch website content
async def handler(
        sql: str,
        params: list
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    base_url = f'https://api.cloudflare.com/client/v4/accounts/{os.getenv("CLOUDFLARE_ACCOUNT_ID")}/d1/database/{os.getenv("CLOUDFLARE_D1_DB_UUID")}/query'

    headers = {
        'Authorization': f'Bearer {os.getenv("CLOUDFLARE_API_TOKEN")}',
        'Content-Type': 'application/json'
    }

    payload = {'sql': sql, 'params': params or []}
    response = requests.post(base_url, headers=headers, json=payload)
    response.raise_for_status()
    # print(response.json()['result'][0]['results'])
    return [types.TextContent(type="text", text=json.dumps(response.json()))]
