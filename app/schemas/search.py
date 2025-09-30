from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from enum import Enum


class SearchType(str, Enum):
    """Supported search types."""

    WEB = "web"
    IMAGE = "image"
    NEWS = "news"
    VIDEO = "video"
    ACADEMIC = "academic"


class ImageSize(str, Enum):
    """Image size filters."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"
    XXLARGE = "xxlarge"
    HUGE = "huge"


class ImageType(str, Enum):
    """Image type filters."""

    CLIPART = "clipart"
    FACE = "face"
    LINEART = "lineart"
    STOCK = "stock"
    PHOTO = "photo"
    ANIMATED = "animated"


class SafeSearch(str, Enum):
    """Safe search levels."""

    OFF = "off"
    MEDIUM = "medium"
    HIGH = "high"


class TimeFilter(str, Enum):
    """Time-based search filters."""

    PAST_DAY = "d"
    PAST_WEEK = "w"
    PAST_MONTH = "m"
    PAST_YEAR = "y"


class BaseSearchRequest(BaseModel):
    """Base search request model."""

    query: str = Field(description="Search query string", min_length=1, max_length=1000)
    num_results: Optional[int] = Field(
        default=10,
        description="Number of search results to return. IMPORTANT: Google Custom Search API has a hard limit of maximum 10 results per request. Use values 1-10 only. For more results, use pagination with start_index (e.g., start_index=11 for next 10 results). Default: 10",
        ge=1,
        le=10,
    )
    start_index: Optional[int] = Field(
        default=1,
        description="Starting index for pagination. Use 1 for first page, 11 for second page (results 11-20), 21 for third page (results 21-30), etc. Maximum start_index is 91 (for results 91-100). Default: 1",
        ge=1,
        le=91,
    )
    safe_search: Optional[SafeSearch] = Field(
        default=SafeSearch.MEDIUM, description="Safe search filter level"
    )
    language: Optional[str] = Field(
        default="en",
        description="Language code for search results (ISO 639-1)",
        pattern=r"^[a-z]{2}$",
    )
    country: Optional[str] = Field(
        default="us",
        description="Country code for search results (ISO 3166-1)",
        pattern=r"^[a-z]{2}$",
    )


class WebSearchRequest(BaseSearchRequest):
    """Web search specific request model."""

    site: Optional[str] = Field(
        default=None,
        description="Restrict results to specific site (e.g., 'reddit.com')",
    )
    file_type: Optional[str] = Field(
        default=None, description="Filter by file type (e.g., 'pdf', 'docx')"
    )
    time_filter: Optional[TimeFilter] = Field(
        default=None, description="Filter results by time period"
    )
    exact_terms: Optional[str] = Field(
        default=None, description="Exact phrase that must appear in results"
    )
    exclude_terms: Optional[str] = Field(
        default=None, description="Terms to exclude from results"
    )


class ImageSearchRequest(BaseSearchRequest):
    """Image search specific request model."""

    image_size: Optional[ImageSize] = Field(
        default=None, description="Filter by image size"
    )
    image_type: Optional[ImageType] = Field(
        default=None, description="Filter by image type"
    )
    color: Optional[str] = Field(
        default=None, description="Filter by dominant color (e.g., 'red', 'blue')"
    )
    usage_rights: Optional[str] = Field(
        default=None, description="Filter by usage rights"
    )


class NewsSearchRequest(BaseSearchRequest):
    """News search specific request model."""

    sort_by: Optional[str] = Field(
        default="date", description="Sort results by 'date' or 'relevance'"
    )
    time_filter: Optional[TimeFilter] = Field(
        default=None, description="Filter news by time period"
    )


class BaseSearchResult(BaseModel):
    """Base search result model."""

    title: str = Field(description="Result title")
    link: HttpUrl = Field(description="Result URL")
    snippet: Optional[str] = Field(
        default=None, description="Result description/snippet"
    )
    display_link: Optional[str] = Field(default=None, description="Display URL")


class WebSearchResult(BaseSearchResult):
    """Web search result model."""

    cached_url: Optional[HttpUrl] = Field(
        default=None, description="Cached version URL"
    )
    file_format: Optional[str] = Field(
        default=None, description="File format if applicable"
    )
    formatted_url: Optional[str] = Field(default=None, description="Formatted URL")
    html_formatted_url: Optional[str] = Field(
        default=None, description="HTML formatted URL"
    )
    html_snippet: Optional[str] = Field(
        default=None, description="HTML formatted snippet"
    )
    html_title: Optional[str] = Field(default=None, description="HTML formatted title")
    mime_type: Optional[str] = Field(default=None, description="MIME type")
    page_map: Optional[Dict[str, Any]] = Field(
        default=None, description="Page metadata"
    )


class ImageSearchResult(BaseSearchResult):
    """Image search result model."""

    image: Optional[Dict[str, Any]] = Field(default=None, description="Image metadata")
    thumbnail_link: Optional[HttpUrl] = Field(default=None, description="Thumbnail URL")
    thumbnail_height: Optional[int] = Field(
        default=None, description="Thumbnail height"
    )
    thumbnail_width: Optional[int] = Field(default=None, description="Thumbnail width")
    context_link: Optional[HttpUrl] = Field(
        default=None, description="Context page URL"
    )


class NewsSearchResult(BaseSearchResult):
    """News search result model."""

    published_date: Optional[datetime] = Field(
        default=None, description="Publication date"
    )
    source: Optional[str] = Field(default=None, description="News source")
    author: Optional[str] = Field(default=None, description="Article author")


class SearchQuery(BaseModel):
    """Search query information."""

    title: Optional[str] = Field(default=None, description="Query title")
    total_results: Optional[str] = Field(
        default=None, description="Total results count"
    )
    search_time: Optional[float] = Field(
        default=None, description="Search time in seconds"
    )
    count: Optional[int] = Field(default=None, description="Number of results returned")
    start_index: Optional[int] = Field(default=None, description="Starting index")
    input_encoding: Optional[str] = Field(default=None, description="Input encoding")
    output_encoding: Optional[str] = Field(default=None, description="Output encoding")
    safe: Optional[str] = Field(default=None, description="Safe search setting")
    cx: Optional[str] = Field(default=None, description="Custom search engine ID")


class SearchInfo(BaseModel):
    """Search metadata."""

    search_time: float = Field(description="Time taken for search in seconds")
    formatted_search_time: str = Field(description="Formatted search time")
    total_results: str = Field(description="Total number of results available")
    formatted_total_results: str = Field(description="Formatted total results")


class Spelling(BaseModel):
    """Spelling correction information."""

    corrected_query: str = Field(description="Corrected search query")
    html_corrected_query: str = Field(description="HTML formatted corrected query")


SearchResult = Union[WebSearchResult, ImageSearchResult, NewsSearchResult]


class BaseSearchResponse(BaseModel):
    """Base search response model."""

    kind: str = Field(description="Response type")
    url: Optional[Dict[str, Any]] = Field(default=None, description="URL template")
    queries: Optional[Dict[str, List[SearchQuery]]] = Field(
        default=None, description="Query information"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Search context"
    )
    search_information: Optional[SearchInfo] = Field(
        default=None, description="Search metadata"
    )
    spelling: Optional[Spelling] = Field(
        default=None, description="Spelling corrections"
    )
    items: List[SearchResult] = Field(default=[], description="Search results")


class WebSearchResponse(BaseSearchResponse):
    """Web search response model."""

    items: List[WebSearchResult] = Field(default=[], description="Web search results")


class ImageSearchResponse(BaseSearchResponse):
    """Image search response model."""

    items: List[ImageSearchResult] = Field(
        default=[], description="Image search results"
    )


class NewsSearchResponse(BaseSearchResponse):
    """News search response model."""

    items: List[NewsSearchResult] = Field(default=[], description="News search results")


class SearchError(BaseModel):
    """Search error model."""

    error: str = Field(description="Error message")
    code: Optional[int] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )


class CachedSearch(BaseModel):
    """Cached search model."""

    id: str = Field(description="Unique search ID")
    query: str = Field(description="Original search query")
    search_type: SearchType = Field(description="Type of search performed")
    results: BaseSearchResponse = Field(description="Cached search results")
    created_at: datetime = Field(description="Cache creation timestamp")
    expires_at: datetime = Field(description="Cache expiration timestamp")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )
