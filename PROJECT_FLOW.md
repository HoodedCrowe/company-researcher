# Company Research Agent — How It Works

## Overview

This agent takes a company name and produces an executive briefing by orchestrating three specialized nodes via **LangGraph**. Each node has a distinct responsibility, and the agent's reasoning is visible in the terminal throughout execution.

```
Input: "Stripe"  →  [Planner]  →  [Researcher]  →  [Synthesizer]  →  Output: stripe_briefing.md
```

---

## Execution Flow

### 1. Planner Node

**Purpose:** Interpret the company name and generate targeted search queries.

**Process:**
1. Receives raw company name from user (e.g., `"Apple"`)
2. Calls Claude to disambiguate (e.g., `"Apple"` → `"Apple Inc, technology company"`)
3. Generates up to 5 search queries targeting:
   - Company overview & founding info
   - Funding & valuation
   - Products & services
   - Leadership team
   - Employee headcount
4. Prioritizes queries for authoritative sources (Crunchbase, LinkedIn, Bloomberg)

**Output:** Interpreted company name + list of search queries with reasoning

---

### 2. Researcher Node

**Purpose:** Execute searches and extract structured facts.

**Process:**
1. Executes each search query via Tavily API
   - Priority queries (targeting major sites) run first
   - Failed queries retry once before marking as failed
2. Checks data sufficiency:
   - Minimum 3 total results required
   - Must have results from authoritative sources
3. If sufficient data exists, calls Claude to extract facts into 6 categories:
   - `overview` | `funding` | `products` | `leadership` | `headcount` | `news`
4. Deduplicates sources and assigns citation indices

**Output:** Structured facts with source URLs, or insufficient data flag

---

### 3. Synthesizer Node

**Purpose:** Generate the final executive briefing.

**Process:**
1. If data insufficient: generates a brief explanation of what's missing
2. If data sufficient: calls Claude to write a 2-3 paragraph executive summary
   - Uses extracted facts as source material
   - Includes inline citations `[1]`, `[2]`, etc.
3. Assembles final `Briefing` object with:
   - Executive summary
   - Key facts by category
   - Numbered source list
   - Any warnings (e.g., failed searches)

**Output:** Complete briefing saved as markdown file

---

## Data Models

| Model | Purpose |
|-------|---------|
| `AgentState` | Carries all data between nodes (queries, results, facts, briefing) |
| `SearchQuery` | Query string + reasoning + priority flag |
| `SearchResult` | Title, URL, snippet, domain from Tavily |
| `CompanyFact` | Categorized fact with source URL and citation index |
| `Briefing` | Final output: summary, facts, sources, warnings |

---

## Terminal Output

```
🤔 Planning research for: Stripe
   Interpreting: "Stripe" → Stripe (fintech/payments company)
   
   Reasoning: I'll search for company overview, funding, products...
   
   → Query 1: "Stripe company overview Crunchbase"
   → Query 2: "Stripe funding valuation 2024"
   → Query 3: "Stripe payments API products"
   → Query 4: "Stripe CEO leadership team"
   → Query 5: "Stripe employee headcount"

🔍 Executing searches...
   ✓ "Stripe company overview Crunchbase": Found 5 results
   ✓ "Stripe funding valuation 2024": Found 4 results
   ✓ "Stripe payments API products": Found 5 results
   ✓ "Stripe CEO leadership team": Found 3 results
   ✓ "Stripe employee headcount": Found 2 results

📊 Extracting facts...
   Found 12 facts across 6 categories

✍️  Synthesizing briefing...

✅ Briefing saved to: output/stripe_briefing.md
```

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Search fails | Retry once, then continue with partial results |
| Too few results (<3) | Mark as insufficient data, explain in output |
| No authoritative sources | Mark as insufficient data |
| Missing fact categories (<2) | Mark as insufficient data |
| API key missing | Exit with clear error message |

---

## Output File Structure

```markdown
# Executive Briefing: Stripe

*Generated: 2025-01-15 14:30:00 UTC*

## Executive Summary
[2-3 paragraphs with inline [N] citations]

## Key Facts
**Overview**
- Founded in 2010, headquartered in San Francisco [1]

**Funding & Valuation**
- Valued at $50 billion (2023) [2]

[...more categories...]

## Sources
1. https://crunchbase.com/organization/stripe
2. https://bloomberg.com/...
```