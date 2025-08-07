# Clock Console

A FastAPI-based web application with async HTTP client capabilities.

## Features

- ⚡ Built with FastAPI for high-performance async API development
- 🔄 Async HTTP client support using httpx for external API integrations
- 🚀 Modern Python 3.13+ with type hints
- 📦 Dependency management with uv

## Dependencies

### Core Dependencies

- **FastAPI** (>=0.116.1): Modern, fast web framework for building APIs with Python
- **Uvicorn** (>=0.35.0): Lightning-fast ASGI server implementation
- **httpx** (>=0.27.0): Fully featured HTTP client with async support, perfect for FastAPI integration
  - Supports both sync and async operations
  - HTTP/1.1 and HTTP/2 support
  - Connection pooling
  - Cookie persistence
  - Automatic content decompression
  - Timeout configuration
  - Built-in retry mechanisms

## Installation

1. Ensure you have Python 3.13 or higher installed
2. Install dependencies using uv:
   ```bash
   uv sync
   ```
   Or manually install:
   ```bash
   uv add fastapi uvicorn httpx
   ```

## Usage

### Running the Development Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Making HTTP Requests with httpx

Example of using httpx in your FastAPI application:

```python
import httpx
from fastapi import FastAPI

app = FastAPI()

# Async example
@app.get("/fetch-data")
async def fetch_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

# Sync example (though async is preferred with FastAPI)
@app.get("/fetch-sync")
def fetch_sync_data():
    with httpx.Client() as client:
        response = client.get("https://api.example.com/data")
        return response.json()
```

## API Endpoints

- `GET /` - Returns a welcome message
- `GET /items/{item_id}` - Returns item details with optional query parameter

## Development

- Linting: `ruff check .`
- Type checking: `mypy main.py`
- Code quality: SonarQube configuration available in `sonar-project.properties`

## Why httpx?

We chose httpx as our HTTP client library because:

1. **Async-first design**: Perfect integration with FastAPI's async nature
2. **Feature-rich**: Supports everything from basic requests to advanced features like HTTP/2
3. **Type hints**: Full type annotation support for better IDE experience
4. **Similar API to requests**: Easy transition for developers familiar with the requests library
5. **Active development**: Well-maintained with regular updates
6. **Connection pooling**: Efficient resource usage for multiple requests

## License

[Add your license information here]
