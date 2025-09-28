from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Custom Search API Settings
    google_api_key: str = Field(
        description="Google Custom Search API key", env="GOOGLE_API_KEY"
    )
    google_cse_id: str = Field(
        description="Google Custom Search Engine ID", env="GOOGLE_CSE_ID"
    )

    # Server Settings
    app_name: str = Field(
        default="MCP Web Search Server", description="Application name"
    )
    app_description: str = Field(
        default="FastAPI MCP server for comprehensive Google web search capabilities",
        description="Application description",
    )
    version: str = Field(default="0.1.0", description="Application version")

    # Search Settings
    default_search_results: int = Field(
        default=10,
        description="Default number of search results to return",
        ge=1,
        le=10,
    )
    max_search_results: int = Field(
        default=10,
        description="Maximum number of search results allowed (Google Custom Search API limit)",
        ge=1,
        le=10,
    )
    cache_ttl_seconds: int = Field(
        default=3600, description="Cache TTL in seconds (1 hour default)", ge=60
    )

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        default=100, description="Rate limit for API requests per minute", ge=1
    )

    # HTTP Client Settings
    http_timeout: int = Field(
        default=30, description="HTTP request timeout in seconds", ge=1, le=300
    )

    # MCP Server Settings
    mcp_mount_path: str = Field(
        default="/mcp", description="Path where MCP server will be mounted"
    )
    enable_cors: bool = Field(default=True, description="Enable CORS middleware")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Global settings instance
settings = Settings()

# Validation
if not settings.google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")
if not settings.google_cse_id:
    raise ValueError("GOOGLE_CSE_ID environment variable is required")

