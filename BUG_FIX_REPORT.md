# Web Search MCP Service - 500 Error Bug Fix Report

## Issue Summary

The Web Search MCP service was returning HTTP 500 "Internal Server Error" responses for certain search requests, specifically when `num_results` parameter exceeded 10.

## Root Cause Analysis

### Problem Identified

- **Primary Issue**: Google Custom Search API has a hard limit of 10 results per request
- **Code Issue**: The service configuration and schema validation allowed up to 100 results (`le=100`)
- **Error Handling**: Poor error handling masked the actual 400 "Bad Request" error from Google API

### Symptoms

- MCP tool calls returning empty responses `{}`
- Docker logs showing: `ERROR:fastapi_mcp.server:Error calling search_web`
- Direct HTTP requests > 10 results failing with 500 errors

### Investigation Results

#### Testing Results:

- ✅ `num_results=10`: Works perfectly
- ❌ `num_results=11+`: Returns 500 error
- ✅ Site queries (`site:scholar.google.com`): Work fine
- ✅ Escape characters and special queries: Work fine
- ✅ Combined queries with ≤10 results: Work fine

#### Direct Google API Testing:

```bash
# This works (returns 10 results)
curl "https://googleapis.com/customsearch/v1?key=XXX&cx=XXX&q=test&num=10"

# This fails with 400 Bad Request
curl "https://googleapis.com/customsearch/v1?key=XXX&cx=XXX&q=test&num=15"
# Returns: {"error": {"code": 400, "message": "Request contains an invalid argument."}}
```

## Fix Implementation

### 1. Schema Validation Fix

**File**: `app/schemas/search.py`

```python
# BEFORE
num_results: Optional[int] = Field(
    default=10,
    description="Number of results to return",
    ge=1, le=100  # ❌ Wrong limit
)

# AFTER
num_results: Optional[int] = Field(
    default=10,
    description="Number of results to return",
    ge=1, le=10   # ✅ Correct Google API limit
)
```

### 2. Configuration Update

**File**: `app/config.py`

```python
# BEFORE
max_search_results: int = Field(
    default=100,
    description="Maximum number of search results allowed",
    ge=1, le=100,
)

# AFTER
max_search_results: int = Field(
    default=10,
    description="Maximum number of search results allowed (Google Custom Search API limit)",
    ge=1, le=10,
)
```

### 3. Error Handling Improvement

**File**: `app/services/google.py`

```python
# Added specific error handling for 400 errors
except httpx.HTTPStatusError as e:
    error_detail = e.response.text if hasattr(e, "response") else str(e)
    # Check if it's a 400 error about invalid num parameter
    if e.response.status_code == 400 and "invalid argument" in error_detail.lower():
        raise Exception(
            f"Invalid search parameters. Google Custom Search API only supports up to 10 results per request. Error: {error_detail}"
        )
    raise Exception(
        f"Google Search API error: {e.response.status_code} - {error_detail}"
    )
```

## Validation of Fix

### Before Fix:

```bash
curl -X POST http://localhost:8500/search/web \
  -H "Content-Type: application/json" \
  -d '{"num_results":15,"query":"test"}'
# Result: 500 Internal Server Error
```

### After Fix:

```bash
curl -X POST http://localhost:8500/search/web \
  -H "Content-Type: application/json" \
  -d '{"num_results":15,"query":"test"}'
# Result: 422 Validation Error with clear message:
# {"detail":[{"type":"less_than_equal","loc":["body","num_results"],"msg":"Input should be less than or equal to 10","input":15,"ctx":{"le":10}}]}

curl -X POST http://localhost:8500/search/web \
  -H "Content-Type: application/json" \
  -d '{"num_results":10,"query":"test"}'
# Result: 200 OK with 10 search results
```

## Impact Assessment

### Positive Impacts:

- ✅ Eliminates 500 errors for invalid `num_results`
- ✅ Provides clear validation error messages
- ✅ Prevents unnecessary API calls to Google
- ✅ Improves user experience with meaningful errors

### Breaking Changes:

- ⚠️ `num_results` now limited to 1-10 instead of 1-100
- ⚠️ Existing clients requesting >10 results will now get 422 instead of 500

### Backward Compatibility:

- ✅ All valid requests (num_results ≤ 10) continue to work
- ✅ Default behavior unchanged (still defaults to 10 results)

## Deployment

The fix was deployed by:

1. Rebuilding the Docker container: `docker compose build mcp-api`
2. Restarting the service: `docker compose up mcp-api -d`

## Recommendations

### For Users:

- Always use `num_results` between 1-10
- For more results, use pagination with `start_index` parameter
- Example for getting 20 results:
  - Request 1: `{"num_results": 10, "start_index": 1}`
  - Request 2: `{"num_results": 10, "start_index": 11}`

### For Future Development:

1. **Add Pagination Helper**: Create a utility function to automatically handle pagination
2. **Documentation Update**: Update API documentation to reflect the 10-result limit
3. **Testing**: Add integration tests for edge cases and API limits
4. **Monitoring**: Add metrics to track validation errors

## Google Custom Search API Limits Reference

- **Results per request**: Maximum 10
- **Requests per day**: 100 (free tier), 10,000+ (paid)
- **Total results**: Up to 100 via pagination (10 requests × 10 results)
- **Start index**: 1-91 (for pagination)

---

**Date**: 2025-09-28  
**Status**: ✅ RESOLVED  
**Severity**: High (caused service failures)  
**Fix Complexity**: Low (configuration change)
