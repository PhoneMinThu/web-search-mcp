# AI Awareness Implementation Summary

## 🎯 Objective

Make AI systems automatically aware that `num_results` has a maximum limit of 10 for the Web Search MCP service.

## 📝 Changes Implemented

### 1. Enhanced Field Descriptions (`app/schemas/search.py`)

```python
num_results: Optional[int] = Field(
    default=10,
    description="Number of search results to return. IMPORTANT: Google Custom Search API has a hard limit of maximum 10 results per request. Use values 1-10 only. For more results, use pagination with start_index (e.g., start_index=11 for next 10 results). Default: 10",
    ge=1, le=10
)

start_index: Optional[int] = Field(
    default=1,
    description="Starting index for pagination. Use 1 for first page, 11 for second page (results 11-20), 21 for third page (results 21-30), etc. Maximum start_index is 91 (for results 91-100). Default: 1",
    ge=1, le=91
)
```

### 2. Detailed Endpoint Documentation (`app/main.py`)

Each search endpoint now includes:

```python
@app.post(
    "/search/web",
    # ... other params
    summary="Search the web using Google Custom Search API",
    description="""Search the web with Google Custom Search API.

    IMPORTANT LIMITATIONS:
    - Maximum 10 results per request (num_results: 1-10)
    - For more results, use pagination with start_index
    - Total limit: 100 results maximum via pagination
    - Example for 20 results: Call twice with start_index=1 then start_index=11

    Use site parameter to restrict to specific domains (e.g., site='reddit.com')
    """
)
```

### 3. Application Description Update (`app/config.py`)

```python
app_description: str = Field(
    default="FastAPI MCP server for Google Custom Search API with web, image, and news search. IMPORTANT: Maximum 10 results per request due to Google API limits. Use pagination with start_index for more results.",
    description="Application description",
)
```

### 4. Comprehensive AI Usage Guide (`AI_USAGE_GUIDE.md`)

Created a detailed guide specifically for AI systems including:

- Critical limitations explanation
- Pagination strategies with code examples
- Best practices and common use cases
- Error handling patterns
- What NOT to do (with examples)

## 🔍 How AI Systems Will See These Changes

### 1. OpenAPI Schema Visibility

When AI systems query the OpenAPI schema, they'll see:

```json
{
  "num_results": {
    "description": "Number of search results to return. IMPORTANT: Google Custom Search API has a hard limit of maximum 10 results per request. Use values 1-10 only. For more results, use pagination with start_index (e.g., start_index=11 for next 10 results). Default: 10",
    "maximum": 10,
    "minimum": 1,
    "default": 10
  }
}
```

### 2. MCP Tool Discovery

When using the MCP protocol, AI systems will receive:

- Tool descriptions with explicit limitations
- Parameter constraints (le=10)
- Usage guidance in descriptions

### 3. Error Messages

If AI systems still attempt >10 results, they get clear feedback:

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "num_results"],
      "msg": "Input should be less than or equal to 10",
      "input": 15
    }
  ]
}
```

## ✅ Verification

### Testing AI Awareness

1. **Schema Discovery**: AI can read maximum=10 from OpenAPI spec
2. **Tool Descriptions**: MCP tools include limitation warnings
3. **Validation Errors**: Clear 422 responses for invalid requests
4. **Documentation**: Comprehensive usage guide available

### Example AI Behavior Expected

```
User: "Find me 50 research papers on AI"

Smart AI Response: "I'll search for AI research papers. Note that each search request can return a maximum of 10 results due to Google API limitations. I'll make multiple paginated requests to get more comprehensive results."

AI Request Pattern:
1. {"query": "AI research papers", "num_results": 10, "start_index": 1}
2. {"query": "AI research papers", "num_results": 10, "start_index": 11}
3. {"query": "AI research papers", "num_results": 10, "start_index": 21}
... (up to 5 requests for 50 results)
```

## 🎯 Benefits Achieved

### For AI Systems

- ✅ Clear constraint understanding through schema
- ✅ Automatic pagination guidance
- ✅ Preventive error avoidance
- ✅ Better user experience messaging

### For Users

- ✅ No more confusing 500 errors
- ✅ AI explains limitations transparently
- ✅ Automatic handling of large result requests
- ✅ Faster responses (no failed attempts)

### For Developers

- ✅ Self-documenting API
- ✅ Reduced support burden
- ✅ Better API adoption
- ✅ Clear usage patterns

## 🚀 Deployment Status

- ✅ Code changes implemented
- ✅ Docker container rebuilt and deployed
- ✅ OpenAPI schema updated with new descriptions
- ✅ MCP tools reflect new limitations
- ✅ Validation working correctly

## 📊 Impact Measurement

Monitor these metrics to confirm AI awareness:

- Reduction in 422 validation errors for num_results > 10
- Increase in pagination usage (start_index > 1)
- Better user satisfaction (fewer failed searches)
- More efficient API usage patterns

---

**Status**: ✅ COMPLETE  
**AI Systems are now fully informed about the 10-result limitation through multiple channels**
