# decision-mind

A demonstration project implementing the Model Context Protocol (MCP), showcasing client-server communication with various functionalities including web content fetching and system monitoring.

## Features

- Web content fetching and parsing
- System information monitoring
- Real-time server-sent events (SSE) communication
- MCP protocol implementation
- Resource management and tool execution

## Requirements

- Python 3.10+
- Dependencies (install via pip):
  - httpx
  - beautifulsoup4
  - uvicorn
  - psutil
  - mcp-sdk

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/decision-mind.git
cd decision-mind
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python server.py
```
The server will start on http://localhost:8000

2. In a separate terminal, run the client:
```bash
python client.py
```

The client will connect to the server and demonstrate various functionalities including:
- Listing available resources
- Reading greeting message
- Fetching system information
- Processing web content

## Protocol Implementation

This project implements the Model Context Protocol (MCP), providing a framework for:
- Server-Sent Events (SSE) based communication
- Resource management
- Tool execution
- Client-server interaction

## License

See the [LICENSE](LICENSE) file for details.
