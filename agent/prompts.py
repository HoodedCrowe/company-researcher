"""Prompt templates for LLM interactions in the research agent."""

PLANNER_PROMPT = """You are a company research planner. Given a company name, you need to:
1. Interpret/disambiguate it (e.g., "Apple" might mean "Apple Inc, the technology company" to avoid confusion with fruit)
2. Generate up to {max_queries} search queries to find comprehensive information

Target these information categories:
- Company overview (founding, headquarters, description)
- Funding and valuation (recent rounds, investors)
- Products and services
- Leadership team (CEO, founders, key executives)
- Employee headcount
- Recent news and developments

IMPORTANT: Prioritize queries that will find results on authoritative sites like:
{priority_domains}

For your first 1-2 queries, explicitly include site names like "Crunchbase" or "LinkedIn" to quickly find authoritative data.

Company to research: "{company_name}"

Respond with valid JSON matching this exact structure:
{{
    "company_interpreted": "Full formal company name",
    "disambiguation_note": "Brief context to add to searches (e.g., 'technology company' or 'fintech startup')",
    "reasoning": "Your overall research strategy explanation",
    "queries": [
        {{"query": "search query text", "reasoning": "why this query", "priority": true/false}}
    ]
}}

Set priority=true for queries targeting authoritative sites. Generate exactly {max_queries} queries."""


EXTRACTION_PROMPT = """Extract key facts about {company_name} from these search results.

{results_text}

Extract facts in these categories:
- overview: Company description, founding date, headquarters, industry
- funding: Funding rounds, valuation, investors
- products: Main products, services, what they do
- leadership: CEO, founders, key executives
- headcount: Number of employees
- news: Recent developments, announcements, news

Respond with valid JSON array of facts:
[
    {{"category": "overview", "fact": "factual statement", "source_url": "url", "source_index": 1}},
    ...
]

Rules:
- Only include facts clearly stated in the sources
- source_index should match the [N] reference number
- Be concise but informative
- Include at least 1 fact per category if available"""


SYNTHESIS_PROMPT = """Write an executive briefing for {company_name}.

Available facts:
{facts_text}

Sources:
{sources_text}

Write 2-3 paragraphs that:
1. Provide a clear overview of the company
2. Highlight key business information (products, funding, size)
3. Note any recent developments or news

Include inline citations using [N] format referring to the source numbers.
Be concise, professional, and informative.
Write in a neutral, factual tone suitable for business research."""