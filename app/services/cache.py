from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import json

from ..schemas.search import CachedSearch, SearchType, BaseSearchResponse
from ..config import settings


class CacheService:
    """Simple in-memory cache service for search results."""

    def __init__(self):
        self._cache: Dict[str, CachedSearch] = {}
        self._search_history: List[Dict[str, Any]] = []

    def _generate_cache_key(
        self, query: str, search_type: SearchType, params: Dict[str, Any] = None
    ) -> str:
        """Generate a unique cache key for the search."""
        cache_data = {
            "query": query.lower().strip(),
            "search_type": search_type.value,
            "params": sorted((params or {}).items()),
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()[:16]

    def get(
        self, query: str, search_type: SearchType, params: Dict[str, Any] = None
    ) -> Optional[BaseSearchResponse]:
        """Get cached search results if they exist and are valid."""
        cache_key = self._generate_cache_key(query, search_type, params)

        if cache_key in self._cache:
            cached_search = self._cache[cache_key]
            if datetime.now() < cached_search.expires_at:
                return cached_search.results
            else:
                # Remove expired entry
                del self._cache[cache_key]

        return None

    def set(
        self,
        query: str,
        search_type: SearchType,
        results: BaseSearchResponse,
        params: Dict[str, Any] = None,
        ttl_seconds: int = None,
    ) -> str:
        """Cache search results with expiration."""
        cache_key = self._generate_cache_key(query, search_type, params)
        ttl = ttl_seconds or settings.cache_ttl_seconds

        now = datetime.now()
        cached_search = CachedSearch(
            id=cache_key,
            query=query,
            search_type=search_type,
            results=results,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl),
            metadata=params,
        )

        self._cache[cache_key] = cached_search

        # Add to search history
        self._search_history.append(
            {
                "query": query,
                "search_type": search_type.value,
                "timestamp": now.isoformat(),
                "cache_key": cache_key,
                "results_count": len(results.items) if hasattr(results, "items") else 0,
            }
        )

        # Keep only last 1000 history entries
        if len(self._search_history) > 1000:
            self._search_history = self._search_history[-1000:]

        return cache_key

    def delete(self, cache_key: str) -> bool:
        """Delete a specific cached entry."""
        if cache_key in self._cache:
            del self._cache[cache_key]
            return True
        return False

    def clear_expired(self) -> int:
        """Remove all expired cache entries and return count removed."""
        now = datetime.now()
        expired_keys = [
            key
            for key, cached_search in self._cache.items()
            if now >= cached_search.expires_at
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def clear_all(self) -> int:
        """Clear all cache entries and return count removed."""
        count = len(self._cache)
        self._cache.clear()
        self._search_history.clear()
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.now()
        valid_entries = sum(
            1
            for cached_search in self._cache.values()
            if now < cached_search.expires_at
        )
        expired_entries = len(self._cache) - valid_entries

        # Calculate cache hit rate from recent history
        recent_history = [
            h
            for h in self._search_history
            if datetime.fromisoformat(h["timestamp"]) > now - timedelta(hours=1)
        ]

        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "total_history_entries": len(self._search_history),
            "recent_searches_1h": len(recent_history),
            "cache_size_bytes": self._estimate_cache_size(),
        }

    def _estimate_cache_size(self) -> int:
        """Rough estimation of cache size in bytes."""
        try:
            # Rough estimation - not exact but gives an idea
            return len(
                json.dumps(
                    {
                        key: {
                            "query": cached_search.query,
                            "search_type": cached_search.search_type.value,
                            "results_count": len(cached_search.results.items)
                            if hasattr(cached_search.results, "items")
                            else 0,
                        }
                        for key, cached_search in self._cache.items()
                    }
                )
            )
        except Exception:
            return 0

    def get_recent_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent search queries."""
        return sorted(
            self._search_history[-limit:], key=lambda x: x["timestamp"], reverse=True
        )

    def get_popular_queries(
        self, limit: int = 20, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get most popular queries within the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_searches = [
            h
            for h in self._search_history
            if datetime.fromisoformat(h["timestamp"]) > cutoff_time
        ]

        # Count query frequency
        query_counts: Dict[str, Dict[str, Any]] = {}
        for search in recent_searches:
            query = search["query"].lower().strip()
            if query in query_counts:
                query_counts[query]["count"] += 1
                query_counts[query]["last_searched"] = max(
                    query_counts[query]["last_searched"], search["timestamp"]
                )
            else:
                query_counts[query] = {
                    "query": search["query"],
                    "count": 1,
                    "search_type": search["search_type"],
                    "last_searched": search["timestamp"],
                }

        # Sort by count and return top queries
        popular = sorted(query_counts.values(), key=lambda x: x["count"], reverse=True)

        return popular[:limit]


# Global cache service instance
cache_service = CacheService()

