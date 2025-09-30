# AI Usage Guide - Web Search MCP Service

## 🤖 For AI Systems: How to Use This Service Properly

This guide is specifically written for AI systems to understand the proper usage patterns and limitations of this MCP Web Search service.

## 🚨 CRITICAL LIMITATIONS

### Maximum Results Constraint

- **HARD LIMIT**: Only 10 results maximum per request
- **Parameter**: `num_results` must be between 1-10
- **Reason**: Google Custom Search API restriction
- **Violation**: Requesting >10 results will return 422 validation error

### Getting More Than 10 Results

Use pagination with `start_index`:

```json
// First 10 results (1-10)
{"query": "AI research", "num_results": 10, "start_index": 1}

// Next 10 results (11-20)
{"query": "AI research", "num_results": 10, "start_index": 11}

// Third page (21-30)
{"query": "AI research", "num_results": 10, "start_index": 21}

// Maximum page (91-100)
{"query": "AI research", "num_results": 10, "start_index": 91}
```

## ✅ Best Practices for AI Systems

### 1. Standard Search Pattern

```json
{
  "query": "your search terms",
  "num_results": 10,
  "site": "optional-domain.com",
  "language": "en",
  "country": "us"
}
```

### 2. Academic/Research Search

```json
{
  "query": "machine learning research",
  "num_results": 10,
  "site": "scholar.google.com"
}
```

### 3. Site-Specific Search

```json
{
  "query": "Python tutorials",
  "num_results": 10,
  "site": "stackoverflow.com"
}
```

### 4. Recent Content

```json
{
  "query": "AI news 2024",
  "num_results": 10,
  "time_filter": "w" // past week
}
```

## 🔄 Pagination Strategy for AI

When users request more than 10 results, automatically implement pagination:

```javascript
// Pseudo-code for AI systems
async function searchWithPagination(query, totalNeeded) {
  const results = [];
  const maxPerRequest = 10;
  const maxTotal = 100; // Google API absolute limit

  const actualTotal = Math.min(totalNeeded, maxTotal);
  const requests = Math.ceil(actualTotal / maxPerRequest);

  for (let i = 0; i < requests; i++) {
    const startIndex = i * maxPerRequest + 1;
    const numResults = Math.min(maxPerRequest, actualTotal - results.length);

    const response = await searchWeb({
      query: query,
      num_results: numResults,
      start_index: startIndex,
    });

    results.push(...response.items);
  }

  return results;
}
```

## 🎯 Common AI Use Cases

### Case 1: Research Papers

```json
{
  "query": "TinyML research papers",
  "num_results": 10,
  "site": "scholar.google.com",
  "language": "en"
}
```

### Case 2: Technical Documentation

```json
{
  "query": "React hooks documentation",
  "num_results": 5,
  "site": "reactjs.org"
}
```

### Case 3: News and Current Events

```json
{
  "query": "artificial intelligence news",
  "num_results": 10,
  "time_filter": "w",
  "language": "en"
}
```

### Case 4: Code Examples

```json
{
  "query": "Python async await examples",
  "num_results": 8,
  "site": "github.com"
}
```

## 🚫 What NOT to Do

### ❌ DON'T Request More Than 10 Results

```json
// This WILL FAIL with 422 error
{
  "query": "search term",
  "num_results": 50 // ERROR: exceeds limit
}
```

### ❌ DON'T Ignore Pagination Limits

```json
// This WILL FAIL with 422 error
{
  "query": "search term",
  "num_results": 10,
  "start_index": 150 // ERROR: max is 91
}
```

### ❌ DON'T Make Too Many Concurrent Requests

- Rate limit: Respect the service's rate limiting
- Use sequential requests for pagination

## 🤖 AI Response Patterns

### When User Asks for Many Results

```
User: "Find me 50 articles about machine learning"

AI Response: "I'll search for machine learning articles. Note that I can get up to 10 results per request due to API limitations, but I can make multiple requests to get more results. Let me start with the first 10..."

[Make paginated requests automatically]
```

### When Explaining Limitations

```
AI Response: "I can search for up to 10 results per request. For more comprehensive results, I can make multiple searches with different start positions to get up to 100 total results."
```

## 🛡️ Error Handling for AI

### Handle 422 Validation Errors

```json
// Error response when num_results > 10
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

### Graceful Degradation

```javascript
// If user requests 50 results
if (requestedResults > 10) {
  // Automatically use pagination or inform user about limitation
  console.log(
    `Requested ${requestedResults} results, but API limit is 10 per request. I'll use pagination to get more results.`
  );
}
```

## 📊 Available Search Types

1. **Web Search** (`/search/web`): General web results
2. **Image Search** (`/search/images`): Image results with metadata
3. **News Search** (`/search/news`): News articles with publication dates

## 🔗 Query Enhancement Tips

### For Better Results

- Use specific keywords
- Include year for recent content: "machine learning 2024"
- Use site restrictions for authoritative sources
- Combine exact phrases with broader terms

### Example Enhanced Queries

```json
{
  "query": "\"large language models\" training techniques 2024",
  "exact_terms": "transformer architecture",
  "exclude_terms": "outdated deprecated",
  "num_results": 10
}
```

## 💡 Remember

1. **Always use `num_results` ≤ 10**
2. **Use pagination for more results**
3. **Leverage site-specific searches**
4. **Respect rate limits**
5. **Handle errors gracefully**
6. **Inform users about pagination when getting many results**

This service is designed to be AI-friendly with clear constraints and predictable behavior. Follow these patterns for optimal results!
