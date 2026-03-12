# SKILL: Web Search Grounding for AI Agents

**Skill ID:** web-search-grounding  
**Category:** AI Agent Design  
**Applies to:** Any agent that generates factual claims  
**Created:** 2026-03-12  
**Last Updated:** 2026-03-12

## What This Skill Does

Reduces hallucination in AI agents by mandating web search before 
answering and requiring citation of sources. All factual claims 
are grounded in verifiable web search results.

## When to Use This Skill

Use this pattern when building AI agents that:
- Generate factual information (destinations, attractions, events, 
  weather)
- Make recommendations based on current/recent information
- Need to cite sources for credibility
- Must avoid fabricating data

Do NOT use for:
- Code generation (no need for web search)
- Creative writing (grounding limits creativity)
- Internal data queries (use RAG instead)

## Implementation Pattern

### 1. Create a Web Search Tool

```python
from agent_framework import tool
import httpx

@tool
async def search_web(
    query: str,
    max_results: int = 5
) -> List[Dict[str, str]]:
    """Search the web and return structured results.
    
    Returns list of dicts with: title, url, snippet.
    """
    # Call search API (Bing, Google, etc.)
    # Handle errors gracefully (return [] on failure)
    # Return structured results
```

**Key requirements:**
- Graceful error handling (missing creds → empty results)
- Structured output (title, url, snippet minimum)
- Timeout protection (10-30 seconds)
- Rate limit handling

### 2. Write a Search-First System Prompt

Include these mandatory sections:

```markdown
## MANDATORY GROUNDING RULES

1. **Search First**: You MUST call the `search_web` tool before
   making any recommendations. Never rely on your training data
   alone.

2. **Citation Required**: Every factual claim MUST reference
   specific URLs from your search results. Format: "According to
   [source](url), ..."

3. **No Fabrication**: If web search returns insufficient
   information, return an empty list or say "I couldn't find
   information about X." NEVER invent data without web evidence.
```

Place in system prompt BEFORE task instructions. Make it visually 
prominent.

### 3. Register Tool with Agent

```python
from agent_framework import Agent
from agent_framework_azure_ai import AzureAIClient

agent = Agent(
    client=AzureAIClient(...),
    instructions=load_system_prompt(),
    tools=[search_web],  # Register tool here
)
```

### 4. Enforce Citation in Output Schema

For structured outputs, require `source_url` fields:

```python
class PointOfInterest(BaseModel):
    name: str
    description: str
    source_url: str  # NOT Optional — enforce citation
```

If source_url is Optional, agents will skip it. Make it required.

### 5. Validate Search Was Called

In system prompt, include example showing search tool call:

```markdown
## EXAMPLE

User: "Find attractions in Paris"

1. Call search_web("top attractions Paris France")
2. Analyze results: Eiffel Tower (wikipedia.org), Louvre
   (louvre.fr)
3. Return: [
     {
       "name": "Eiffel Tower",
       "description": "Iconic iron tower...",
       "source_url": "https://en.wikipedia.org/wiki/Eiffel_Tower"
     }
   ]
```

## Anti-Patterns to Avoid

❌ **Making search optional**: "If you can't find information, use 
your knowledge"
- Encourages hallucination fallback

❌ **Accepting fabricated URLs**: Agent returns 
"https://example.com/made-up-page"
- Validate URLs match search results (future enhancement)

❌ **Generic citations**: "According to various sources..."
- Require specific URLs

❌ **Crashing on search errors**: Raise exception if Bing API fails
- Return empty results, log warning

## Testing Strategy

1. **Unit test search tool**: Mock API, verify error handling
2. **Prompt engineering test**: Check system prompt includes 
   grounding rules
3. **Integration test**: Verify agent calls search before answering
4. **Citation test**: Validate all outputs have source_url

Example assertion:
```python
assert all(poi.source_url for poi in pois), \
    "All POIs must have source_url"
```

## Real-World Application

This skill is used in the travel agent project for:
- **General Agent**: Destination recommendations (search "best 
  destinations for {interests}")
- **POI Agent**: Attraction discovery (search "top things to do in 
  {city}")
- **Event Agent**: Festival finding (search "events in {city} 
  {month}")
- **Weather Agent**: Historical weather (search "average weather 
  {city} {month}")

See `src/agents/` and `data/prompts/` for implementations.

## Edge Cases

**No search results**: Return empty list/None with log message. 
NEVER fabricate.

**Search API down**: Graceful degradation — return empty results, 
don't crash entire pipeline.

**Stale information**: Accept limitation. Web search grounding is 
current but not real-time.

**Conflicting sources**: Prompt can instruct: "If sources conflict, 
note the discrepancy or choose the most authoritative source."

## Related Skills

- **API Error Handling**: Robust HTTP client patterns
- **Prompt Engineering**: Clear instruction writing
- **Agent Testing**: Validation strategies

## References

- `src/agents/tools/web_search.py` — Search tool implementation
- `data/prompts/general-agent/system.md` — Example grounding prompt
- `.squad/decisions/inbox/batty-agent-framework-pattern.md` — 
  Integration pattern
