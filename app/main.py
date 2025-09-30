import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP

from .config import settings
from .schemas.search import (
    ImageSearchRequest,
    ImageSearchResponse,
    NewsSearchRequest,
    NewsSearchResponse,
    SearchType,
    WebSearchRequest,
    WebSearchResponse,
)
from .services.cache import cache_service
from .services.google import search_service

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.version,
)

if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Health check
@app.get("/health", tags=["system"], operation_id="health_check")
async def health_check():
    return {"status": "ok", "version": settings.version}


# Cache endpoints (exposed as MCP resources/tools too)
@app.get("/cache/stats", tags=["cache"], operation_id="cache_stats")
async def cache_stats():
    return cache_service.get_stats()


@app.get("/cache/recent", tags=["cache"], operation_id="cache_recent")
async def cache_recent(limit: int = 50):
    return cache_service.get_recent_queries(limit=limit)


@app.get("/cache/popular", tags=["cache"], operation_id="cache_popular")
async def cache_popular(limit: int = 20, hours: int = 24):
    return cache_service.get_popular_queries(limit=limit, hours=hours)


@app.delete("/cache/clear", tags=["cache"], operation_id="cache_clear")
async def cache_clear(all: bool = False):
    if all:
        count = cache_service.clear_all()
        return {"cleared": count, "scope": "all"}
    removed = cache_service.clear_expired()
    return {"cleared": removed, "scope": "expired"}


# Search endpoints
@app.post(
    "/search/web",
    response_model=WebSearchResponse,
    tags=["search"],
    operation_id="search_web",
    summary="Search the web using Google Custom Search API",
    description="""Search the web with Google Custom Search API. 
    
    IMPORTANT LIMITATIONS:
    - Maximum 10 results per request (num_results: 1-10)
    - For more results, use pagination with start_index
    - Total limit: 100 results maximum via pagination
    - Example for 20 results: Call twice with start_index=1 then start_index=11
    
    Use site parameter to restrict to specific domains (e.g., site='reddit.com')
    """,
)
async def search_web_endpoint(req: WebSearchRequest):
    cached = cache_service.get(req.query, SearchType.WEB, req.model_dump())
    if cached:
        return cached
    resp = await search_service.search_web(req)
    cache_service.set(req.query, SearchType.WEB, resp, req.model_dump())
    return resp


@app.post(
    "/search/images",
    response_model=ImageSearchResponse,
    tags=["search"],
    operation_id="search_images",
    summary="Search for images using Google Custom Search API",
    description="""Search for images with Google Custom Search API.
    
    IMPORTANT LIMITATIONS:
    - Maximum 10 results per request (num_results: 1-10)
    - For more results, use pagination with start_index
    - Total limit: 100 results maximum via pagination
    
    Additional image-specific filters available: image_size, image_type, color
    """,
)
async def search_images_endpoint(req: ImageSearchRequest):
    cached = cache_service.get(req.query, SearchType.IMAGE, req.model_dump())
    if cached:
        return cached
    resp = await search_service.search_images(req)
    cache_service.set(req.query, SearchType.IMAGE, resp, req.model_dump())
    return resp


@app.post(
    "/search/news",
    response_model=NewsSearchResponse,
    tags=["search"],
    operation_id="search_news",
    summary="Search for news articles using Google Custom Search API",
    description="""Search for news articles with Google Custom Search API.
    
    IMPORTANT LIMITATIONS:
    - Maximum 10 results per request (num_results: 1-10)
    - For more results, use pagination with start_index
    - Total limit: 100 results maximum via pagination
    
    News results can be sorted by 'date' or 'relevance' and filtered by time period
    """,
)
async def search_news_endpoint(req: NewsSearchRequest):
    cached = cache_service.get(req.query, SearchType.NEWS, req.model_dump())
    if cached:
        return cached
    resp = await search_service.search_news(req)
    cache_service.set(req.query, SearchType.NEWS, resp, req.model_dump())
    return resp


# Mount MCP server (HTTP transport)
# Let FastAPI MCP auto-discover all endpoints and convert them to MCP tools
_mcp = FastApiMCP(
    app,
    name=settings.app_name,
    description=settings.app_description,
    describe_all_responses=True,
    describe_full_response_schema=True,
)
_mcp.mount()


def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8500, reload=True)


if __name__ == "__main__":
    main()
