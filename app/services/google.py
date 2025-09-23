import asyncio
import hashlib
from typing import Dict, List, Any, Union
from datetime import datetime, timedelta
import httpx
import json

from ..config import settings
from ..schemas.search import (
    WebSearchRequest,
    ImageSearchRequest,
    NewsSearchRequest,
    WebSearchResponse,
    ImageSearchResponse,
    NewsSearchResponse,
    WebSearchResult,
    ImageSearchResult,
    NewsSearchResult,
    SearchType,
    SearchInfo,
)


class GoogleSearchService:
    """Google Custom Search API service with caching and rate limiting."""

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=settings.http_timeout,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=100),
        )
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._request_timestamps: List[datetime] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    def _generate_cache_key(
        self, search_type: SearchType, params: Dict[str, Any]
    ) -> str:
        """Generate a unique cache key for the search request."""
        cache_data = {
            "search_type": search_type.value,
            "params": sorted(params.items()),
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _is_cached_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cached entry is still valid."""
        if not cache_entry:
            return False
        expires_at = datetime.fromisoformat(cache_entry["expires_at"])
        return datetime.now() < expires_at

    async def _rate_limit_check(self) -> None:
        """Enforce rate limiting."""
        now = datetime.now()
        # Remove timestamps older than 1 minute
        self._request_timestamps = [
            ts for ts in self._request_timestamps if now - ts < timedelta(minutes=1)
        ]

        if len(self._request_timestamps) >= settings.rate_limit_requests_per_minute:
            sleep_time = 60 - (now - self._request_timestamps[0]).seconds
            await asyncio.sleep(sleep_time)

        self._request_timestamps.append(now)

    def _build_search_params(
        self, request: Union[WebSearchRequest, ImageSearchRequest, NewsSearchRequest]
    ) -> Dict[str, str]:
        """Build search parameters from request."""
        params = {
            "key": settings.google_api_key,
            "cx": settings.google_cse_id,
            "q": request.query,
            "num": str(request.num_results or settings.default_search_results),
            "start": str(request.start_index or 1),
            "safe": request.safe_search.value if request.safe_search else "medium",
            "lr": f"lang_{request.language}" if request.language else "lang_en",
            "gl": request.country or "us",
        }

        if isinstance(request, WebSearchRequest):
            if request.site:
                params["q"] += f" site:{request.site}"
            if request.file_type:
                params["q"] += f" filetype:{request.file_type}"
            if request.exact_terms:
                params["q"] += f' "{request.exact_terms}"'
            if request.exclude_terms:
                params["q"] += f" -{request.exclude_terms}"
            if request.time_filter:
                params["dateRestrict"] = request.time_filter.value

        elif isinstance(request, ImageSearchRequest):
            params["searchType"] = "image"
            if request.image_size:
                params["imgSize"] = request.image_size.value
            if request.image_type:
                params["imgType"] = request.image_type.value
            if request.color:
                params["imgColorType"] = request.color
            if request.usage_rights:
                params["rights"] = request.usage_rights

        elif isinstance(request, NewsSearchRequest):
            params["tbm"] = "nws"  # News search
            if request.sort_by == "date":
                params["sort"] = "date"
            if request.time_filter:
                params["tbs"] = f"qdr:{request.time_filter.value}"

        return {k: v for k, v in params.items() if v is not None}

    def _parse_web_results(self, items: List[Dict[str, Any]]) -> List[WebSearchResult]:
        """Parse web search results."""
        results = []
        for item in items:
            try:
                result = WebSearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet"),
                    display_link=item.get("displayLink"),
                    cached_url=item.get("cacheId"),
                    file_format=item.get("fileFormat"),
                    formatted_url=item.get("formattedUrl"),
                    html_formatted_url=item.get("htmlFormattedUrl"),
                    html_snippet=item.get("htmlSnippet"),
                    html_title=item.get("htmlTitle"),
                    mime_type=item.get("mime"),
                    page_map=item.get("pagemap"),
                )
                results.append(result)
            except Exception:
                # Log error but continue processing other results
                continue
        return results

    def _parse_image_results(
        self, items: List[Dict[str, Any]]
    ) -> List[ImageSearchResult]:
        """Parse image search results."""
        results = []
        for item in items:
            try:
                result = ImageSearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet"),
                    display_link=item.get("displayLink"),
                    image=item.get("image"),
                    thumbnail_link=item.get("image", {}).get("thumbnailLink")
                    if item.get("image")
                    else None,
                    thumbnail_height=item.get("image", {}).get("thumbnailHeight")
                    if item.get("image")
                    else None,
                    thumbnail_width=item.get("image", {}).get("thumbnailWidth")
                    if item.get("image")
                    else None,
                    context_link=item.get("image", {}).get("contextLink")
                    if item.get("image")
                    else None,
                )
                results.append(result)
            except Exception:
                continue
        return results

    def _parse_news_results(
        self, items: List[Dict[str, Any]]
    ) -> List[NewsSearchResult]:
        """Parse news search results."""
        results = []
        for item in items:
            try:
                # Try to extract published date from pagemap or other sources
                published_date = None
                if "pagemap" in item and "newsarticle" in item["pagemap"]:
                    date_str = item["pagemap"]["newsarticle"][0].get("datepublished")
                    if date_str:
                        try:
                            published_date = datetime.fromisoformat(
                                date_str.replace("Z", "+00:00")
                            )
                        except Exception:
                            pass

                result = NewsSearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet"),
                    display_link=item.get("displayLink"),
                    published_date=published_date,
                    source=item.get("displayLink"),
                    author=item.get("pagemap", {})
                    .get("newsarticle", [{}])[0]
                    .get("author")
                    if item.get("pagemap")
                    else None,
                )
                results.append(result)
            except Exception:
                continue
        return results

    async def _make_search_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Make the actual search request to Google API."""
        await self._rate_limit_check()

        try:
            response = await self.http_client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e, "response") else str(e)
            raise Exception(
                f"Google Search API error: {e.response.status_code} - {error_detail}"
            )
        except httpx.RequestError as e:
            raise Exception(f"Request error: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")

    async def search_web(self, request: WebSearchRequest) -> WebSearchResponse:
        """Perform web search."""
        params = self._build_search_params(request)
        cache_key = self._generate_cache_key(SearchType.WEB, params)

        # Check cache first
        if cache_key in self._cache and self._is_cached_valid(self._cache[cache_key]):
            cached_data = self._cache[cache_key]["data"]
            return WebSearchResponse.model_validate(cached_data)

        # Make API request
        try:
            data = await self._make_search_request(params)

            # Parse results
            items = data.get("items", [])
            parsed_results = self._parse_web_results(items)

            # Build response
            search_info = None
            if "searchInformation" in data:
                si = data["searchInformation"]
                search_info = SearchInfo(
                    search_time=si.get("searchTime", 0.0),
                    formatted_search_time=si.get("formattedSearchTime", "0.00"),
                    total_results=si.get("totalResults", "0"),
                    formatted_total_results=si.get("formattedTotalResults", "0"),
                )

            response = WebSearchResponse(
                kind=data.get("kind", "customsearch#search"),
                url=data.get("url"),
                queries=data.get("queries"),
                context=data.get("context"),
                search_information=search_info,
                items=parsed_results,
            )

            # Cache the response
            self._cache[cache_key] = {
                "data": response.model_dump(),
                "expires_at": (
                    datetime.now() + timedelta(seconds=settings.cache_ttl_seconds)
                ).isoformat(),
            }

            return response

        except Exception as e:
            raise Exception(f"Web search failed: {str(e)}")

    async def search_images(self, request: ImageSearchRequest) -> ImageSearchResponse:
        """Perform image search."""
        params = self._build_search_params(request)
        cache_key = self._generate_cache_key(SearchType.IMAGE, params)

        # Check cache first
        if cache_key in self._cache and self._is_cached_valid(self._cache[cache_key]):
            cached_data = self._cache[cache_key]["data"]
            return ImageSearchResponse.model_validate(cached_data)

        try:
            data = await self._make_search_request(params)

            # Parse results
            items = data.get("items", [])
            parsed_results = self._parse_image_results(items)

            # Build response
            search_info = None
            if "searchInformation" in data:
                si = data["searchInformation"]
                search_info = SearchInfo(
                    search_time=si.get("searchTime", 0.0),
                    formatted_search_time=si.get("formattedSearchTime", "0.00"),
                    total_results=si.get("totalResults", "0"),
                    formatted_total_results=si.get("formattedTotalResults", "0"),
                )

            response = ImageSearchResponse(
                kind=data.get("kind", "customsearch#search"),
                url=data.get("url"),
                queries=data.get("queries"),
                context=data.get("context"),
                search_information=search_info,
                items=parsed_results,
            )

            # Cache the response
            self._cache[cache_key] = {
                "data": response.model_dump(),
                "expires_at": (
                    datetime.now() + timedelta(seconds=settings.cache_ttl_seconds)
                ).isoformat(),
            }

            return response

        except Exception as e:
            raise Exception(f"Image search failed: {str(e)}")

    async def search_news(self, request: NewsSearchRequest) -> NewsSearchResponse:
        """Perform news search."""
        params = self._build_search_params(request)
        cache_key = self._generate_cache_key(SearchType.NEWS, params)

        # Check cache first
        if cache_key in self._cache and self._is_cached_valid(self._cache[cache_key]):
            cached_data = self._cache[cache_key]["data"]
            return NewsSearchResponse.model_validate(cached_data)

        try:
            data = await self._make_search_request(params)

            # Parse results
            items = data.get("items", [])
            parsed_results = self._parse_news_results(items)

            # Build response
            search_info = None
            if "searchInformation" in data:
                si = data["searchInformation"]
                search_info = SearchInfo(
                    search_time=si.get("searchTime", 0.0),
                    formatted_search_time=si.get("formattedSearchTime", "0.00"),
                    total_results=si.get("totalResults", "0"),
                    formatted_total_results=si.get("formattedTotalResults", "0"),
                )

            response = NewsSearchResponse(
                kind=data.get("kind", "customsearch#search"),
                url=data.get("url"),
                queries=data.get("queries"),
                context=data.get("context"),
                search_information=search_info,
                items=parsed_results,
            )

            # Cache the response
            self._cache[cache_key] = {
                "data": response.model_dump(),
                "expires_at": (
                    datetime.now() + timedelta(seconds=settings.cache_ttl_seconds)
                ).isoformat(),
            }

            return response

        except Exception as e:
            raise Exception(f"News search failed: {str(e)}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        valid_entries = sum(
            1 for entry in self._cache.values() if self._is_cached_valid(entry)
        )

        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries,
            "recent_requests": len(self._request_timestamps),
        }

    def clear_cache(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


# Global service instance
search_service = GoogleSearchService()

