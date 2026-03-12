# data/prompts/ — Agent System Prompts

This folder stores **system prompts for AI agents**. These are version-controlled artifacts that define agent behavior at runtime.

## Organization

Prompts are organized by agent name:

```
data/prompts/
├── general/
│   └── system.md           # General Agent: destination matching
├── poi/
│   └── system.md           # POI Agent: points of interest discovery
├── event/
│   └── system.md           # Event Agent: events and festivals
└── weather/
    └── system.md           # Weather Agent: historical weather
```

## Conventions

- **Use Markdown (.md)** for readability and version control
- **One file per purpose:** system.md for system instructions, policy.md for policies, etc.
- **Clear, concise prompts:** Agent behavior should be explicit and unambiguous
- **Include examples:** Show agents what good reasoning looks like
- **Mention tools:** Document which tools agents have (e.g., search_web)
- **Grounding:** All prompts emphasize the mandatory use of web search before reasoning

## Typical System Prompt Structure

```markdown
# General Agent System Prompt

You are a destination-matching agent. Your role is to recommend travel destinations based on customer profiles.

## Your Tools

- search_web(query) — Search for destination information using Bing Web Search

## Your Task

Given a customer profile with interests, budget, and travel style:
1. Search for 3-5 destinations that match the profile
2. For each destination, provide:
   - Name and location
   - Why it matches the customer interests
   - Brief description
   - Source URL from your search

## Important

- ALWAYS use search_web before suggesting destinations
- Never fabricate facts about destinations
- Ground all recommendations in web search results
- Include source URLs for all information

## Examples

[Include 1-2 examples of good output]
```

## Loading Prompts in Code

Agents load prompts by path:

```python
# In src/agents/general_agent.py
with open("data/prompts/general/system.md", "r") as f:
    system_prompt = f.read()

agent = Agent(
    name="general-agent",
    system_prompt=system_prompt,
    ...
)
```

## Editing Prompts

1. Edit the .md file directly
2. Test by running the agent and checking output
3. Commit changes to git (prompts are version-controlled)
4. Document significant prompt changes in PR descriptions

## Grounding Pattern

All prompts emphasize **search-first reasoning**:

```markdown
## Mandatory Grounding

- ALWAYS call search_web() first
- Reason only over search results
- Include source URLs for all facts
- Do not hallucinate or guess
```

This prevents agents from making up facts and ensures all recommendations are factual.

## Conventions

- Keep prompts concise (usually under 500 words)
- Be explicit about expected outputs
- Document tool behavior clearly
- Use formatting for clarity (headers, lists, examples)

## Relationship to Code

- Prompts are **artifacts**, not code
- Store in data/prompts/, not in Python files
- Load at agent initialization, not hard-coded
- Easy to diff, review, and version-control

## See Also

- [../README.md](../README.md) — Data folder overview
- [../../src/agents/README.md](../../src/agents/README.md) — Agent implementation
- [../../docs/architecture.md](../../docs/architecture.md) — System design
