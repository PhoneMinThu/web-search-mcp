# MCP Web Search Server

A comprehensive FastAPI MCP (Model Context Protocol) server for Google web search with full search capabilities including web, image, and news search.

## Features

- **FastAPI MCP Integration**: All FastAPI endpoints are automatically exposed as MCP tools
- **Comprehensive Search**: Web, image, and news search via Google Custom Search API
- **Advanced Filtering**: Support for time filters, safe search, file types, image sizes, and more
- **Caching & Performance**: Built-in caching with TTL and rate limiting
- **Full MCP Compliance**: Works with any MCP-compatible AI agent or client
- **Authentication Ready**: Supports FastAPI authentication mechanisms

## Architecture

The server leverages `fastapi-mcp` which automatically converts your FastAPI endpoints into MCP tools, making them accessible to AI agents without additional configuration.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Agent      │───▶│   FastAPI MCP    │───▶│   Google APIs   │
│  (MCP Client)   │    │     Server       │    │  (Custom Search)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   Cache Layer    │
                        │  (In-Memory)     │
                        └──────────────────┘
```

## Installation

1. **Clone and Setup Environment**:
```bash
cd /media/phonemt/linux_data/unix_dev/mcp
source .venv/bin/activate
```

2. **Install Dependencies**:
```bash
uv pip install -r requirements.txt
# Or install from pyproject.toml
uv sync
```

3. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env with your Google API credentials
```

## Configuration

### Required Environment Variables

```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
```

### Getting API Credentials

1. **Google Custom Search API Key**:
   - Go to [Google Cloud Console](https://console.developers.google.com/)
   - Create a new project or select existing
   - Enable \"Custom Search API\"
   - Create credentials (API Key)

2. **Custom Search Engine ID**:
   - Go to [Google Custom Search Engine](https://cse.google.com/)
   - Create a new search engine
   - Configure to search the entire web
   - Copy the Search Engine ID

### Optional Settings

```env
DEFAULT_SEARCH_RESULTS=10
MAX_SEARCH_RESULTS=100
CACHE_TTL_SECONDS=3600
RATE_LIMIT_REQUESTS_PER_MINUTE=100
HTTP_TIMEOUT=30
MCP_MOUNT_PATH=/mcp
ENABLE_CORS=true
```

## Usage

### Starting the Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the built-in runner
python -m app.main
```

### MCP Integration

The server automatically exposes the following MCP tools:

#### Search Tools
- `search_web`: Web search with advanced filtering
- `search_images`: Image search with size, type, and color filters  
- `search_news`: News search with time-based filtering

#### Cache Management Tools
- `cache_stats`: Get cache statistics
- `cache_recent`: View recent search queries
- `cache_popular`: Get most popular search queries
- `cache_clear`: Clear expired or all cache entries

#### System Tools
- `health_check`: Server health status

### API Endpoints

All endpoints are also available as standard REST API:

- `POST /search/web` - Web search
- `POST /search/images` - Image search  
- `POST /search/news` - News search
- `GET /cache/stats` - Cache statistics
- `GET /cache/recent` - Recent queries
- `GET /cache/popular` - Popular queries
- `DELETE /cache/clear` - Clear cache
- `GET /health` - Health check

### Example Search Requests

**Web Search**:
```json
{
  \"query\": \"python machine learning\",
  \"num_results\": 10,
  \"site\": \"github.com\",
  \"file_type\": \"pdf\",
  \"time_filter\": \"m\",
  \"safe_search\": \"medium\"
}
```

**Image Search**:
```json
{
  \"query\": \"sunset mountains\",
  \"num_results\": 20,
  \"image_size\": \"large\",
  \"image_type\": \"photo\",
  \"color\": \"orange\"
}
```

**News Search**:
```json
{
  \"query\": \"artificial intelligence\",
  \"num_results\": 15,
  \"sort_by\": \"date\",
  \"time_filter\": \"w\"
}
```

## MCP Client Usage

Connect any MCP-compatible client to:
- **HTTP Transport**: `http://localhost:8000/mcp`
- **WebSocket**: `ws://localhost:8000/mcp` (if enabled)

The client will automatically discover all available tools and their schemas.

## Development

### Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI app and MCP mounting
├── config.py            # Settings and environment config
├── schemas/
│   ├── __init__.py
│   └── search.py        # Pydantic models for requests/responses
├── services/
│   ├── __init__.py
│   ├── google.py        # Google Custom Search API service
│   └── cache.py         # Cache management service
└── mcp_layers/          # Reserved for custom MCP extensions
    ├── __init__.py
    ├── tools.py         # Custom MCP tools (if needed)
    ├── resources.py     # MCP resources
    └── prompts.py       # MCP prompts
```

### Adding New Search Types

1. Add new enum to `SearchType` in `schemas/search.py`
2. Create request/response models
3. Implement search logic in `services/google.py`
4. Add endpoint in `main.py`
5. The MCP tool will be automatically available!

### Error Handling

The server includes comprehensive error handling:
- Rate limiting with exponential backoff
- API quota management
- Cache invalidation on errors
- Graceful degradation

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync
CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]
```

### Production Considerations

- Use environment-based configuration
- Enable authentication if needed
- Configure rate limiting based on API quotas
- Set up monitoring and logging
- Use a production ASGI server (uvicorn with gunicorn)

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## Support

For issues and questions:
- Check the [FastAPI MCP documentation](https://github.com/jlowin/fastapi-mcp)
- Review Google Custom Search API limits
- Create an issue in this repository