"""LangGraph node implementations for the research agent."""

import json
import os

from anthropic import Anthropic

from agent.state import AgentState
from config import Config
from models.schemas import (
    Briefing,
    CompanyFact,
    PlannerOutput,
)
from agent.prompts import EXTRACTION_PROMPT, PLANNER_PROMPT, SYNTHESIS_PROMPT
from search.tavily import SearchError, TavilySearch
from utils.output import (
    print_facts_summary,
    print_header,
    print_query,
    print_reasoning,
    print_search_result,
    print_search_retry,
)


def get_anthropic_client() -> Anthropic:
    """Get Anthropic client instance."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return Anthropic(api_key=api_key)


def planner_node(state: AgentState) -> dict:
    """
    Planner node: Interprets company name and generates search queries.
    
    Responsibilities:
    - Disambiguate company name (e.g., "Apple" -> "Apple Inc technology company")
    - Generate targeted search queries prioritizing authoritative sources
    - Provide reasoning for research approach
    """
    print_header(f"Planning research for: {state.company_name_raw}", "🤔")

    client = get_anthropic_client()

    prompt = PLANNER_PROMPT.format(
        max_queries=Config.MAX_SEARCH_QUERIES,
        priority_domains=', '.join(Config.PRIORITY_DOMAINS),
        company_name=state.company_name_raw
    )

    response = client.messages.create(
        model=Config.ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = response.content[0].text
    
    # Parse JSON response (handle potential markdown code blocks)
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    parsed = json.loads(response_text.strip())
    planner_output = PlannerOutput(**parsed)
    
    # Print reasoning
    print(f"   Interpreting: \"{state.company_name_raw}\" → {planner_output.company_interpreted}")
    if planner_output.disambiguation_note:
        print(f"   Context: {planner_output.disambiguation_note}")
    print()
    print_reasoning(f"Reasoning: {planner_output.reasoning}")
    print()
    
    # Print queries
    for i, query in enumerate(planner_output.queries, 1):
        print_query(i, query.query)
    
    return {
        "company_name_interpreted": planner_output.company_interpreted,
        "disambiguation_note": planner_output.disambiguation_note,
        "planning_reasoning": planner_output.reasoning,
        "search_queries": planner_output.queries,
    }


def researcher_node(state: AgentState) -> dict:
    """
    Researcher node: Executes searches and extracts structured facts.
    
    Responsibilities:
    - Execute Tavily searches with retry logic
    - Extract structured facts using LLM
    - Track sources for citations
    - Assess data sufficiency
    """
    print_header("Executing searches...", "🔍")
    
    search_client = TavilySearch()
    all_results = []
    failed_queries = []
    warnings = []
    
    # Execute searches (priority queries first)
    priority_queries = [q for q in state.search_queries if q.priority]
    other_queries = [q for q in state.search_queries if not q.priority]
    ordered_queries = priority_queries + other_queries
    
    for query in ordered_queries:
        try:
            results = search_client.search(query.query)
            all_results.extend(results)
            print_search_result(query.query, len(results), success=True)
        except SearchError:
            # Will retry once inside search method, this means final failure
            print_search_retry(query.query)
            try:
                results = search_client.search(query.query)
                all_results.extend(results)
                print_search_result(query.query, len(results), success=True, retry=True)
            except SearchError:
                failed_queries.append(query.query)
                warnings.append(f"Search failed for: {query.query}")
                print_search_result(query.query, 0, success=False)
    
    # Check data sufficiency
    sufficient_data = True
    insufficiency_reason = ""
    
    if len(all_results) < Config.MIN_TOTAL_RESULTS:
        sufficient_data = False
        insufficiency_reason = f"Only found {len(all_results)} results (minimum: {Config.MIN_TOTAL_RESULTS})"
    
    # Check for priority domain results
    priority_results = [r for r in all_results if search_client.is_priority_domain(r.domain)]
    if len(priority_results) == 0 and len(all_results) < 5:
        sufficient_data = False
        insufficiency_reason = "No results from authoritative sources (Crunchbase, LinkedIn, etc.)"
    
    if not sufficient_data:
        return {
            "search_results": all_results,
            "sufficient_data": False,
            "insufficiency_reason": insufficiency_reason,
            "failed_queries": failed_queries,
            "warnings": warnings,
            "facts": [],
            "sources": [],
        }
    
    # Extract facts using LLM
    print_header("Extracting facts...", "📊")
    
    client = get_anthropic_client()
    
    # Deduplicate sources and create mapping
    unique_sources = []
    seen_urls = set()
    for result in all_results:
        if result.url not in seen_urls:
            unique_sources.append(result.url)
            seen_urls.add(result.url)
    
    # Prepare search results for LLM
    results_text = "\n\n".join([
        f"Source [{unique_sources.index(r.url) + 1}]: {r.url}\nTitle: {r.title}\nContent: {r.snippet}"
        for r in all_results if r.url in unique_sources
    ])

    extraction_prompt = EXTRACTION_PROMPT.format(
        company_name=state.company_name_interpreted,
        results_text=results_text
    )

    response = client.messages.create(
        model=Config.ANTHROPIC_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": extraction_prompt}]
    )
    
    response_text = response.content[0].text
    
    # Parse JSON response
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    facts_data = json.loads(response_text.strip())
    facts = [CompanyFact(**f) for f in facts_data]
    
    # Check category coverage
    categories_found = set(f.category for f in facts)
    if len(categories_found) < Config.MIN_FACT_CATEGORIES:
        sufficient_data = False
        insufficiency_reason = f"Only found {len(categories_found)} fact categories (minimum: {Config.MIN_FACT_CATEGORIES})"
    
    print_facts_summary(facts)
    
    return {
        "search_results": all_results,
        "facts": facts,
        "sources": unique_sources,
        "sufficient_data": sufficient_data,
        "insufficiency_reason": insufficiency_reason,
        "failed_queries": failed_queries,
        "warnings": warnings,
    }


def synthesizer_node(state: AgentState) -> dict:
    """
    Synthesizer node: Generates final briefing with citations.
    
    Responsibilities:
    - Generate 2-3 paragraph executive summary
    - Include inline citations [N]
    - Handle insufficient data gracefully
    """
    print_header("Synthesizing briefing...", "✍️ ")
    
    client = get_anthropic_client()
    warnings = list(state.warnings)
    
    if not state.sufficient_data:
        # Generate insufficient data response
        briefing = Briefing(
            company_name=state.company_name_interpreted or state.company_name_raw,
            executive_summary=f"Insufficient data available to generate a comprehensive briefing for {state.company_name_interpreted or state.company_name_raw}. {state.insufficiency_reason}.",
            key_facts=state.facts,
            sources=state.sources,
            partial_results=True,
            warnings=warnings + [state.insufficiency_reason] if state.insufficiency_reason else warnings,
        )
        return {"briefing": briefing}
    
    # Prepare facts for synthesis
    facts_text = "\n".join([
        f"- [{f.category}] {f.fact} (source: [{f.source_index}])"
        for f in state.facts
    ])

    sources_text = "\n".join([
        f"[{i}] {url}" for i, url in enumerate(state.sources, 1)
    ])

    synthesis_prompt = SYNTHESIS_PROMPT.format(
        company_name=state.company_name_interpreted,
        facts_text=facts_text,
        sources_text=sources_text
    )

    response = client.messages.create(
        model=Config.ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": synthesis_prompt}]
    )
    
    executive_summary = response.content[0].text.strip()
    
    # Add warning if there were failed queries
    if state.failed_queries:
        warnings.append(f"Some searches failed: {', '.join(state.failed_queries)}")
    
    briefing = Briefing(
        company_name=state.company_name_interpreted or state.company_name_raw,
        executive_summary=executive_summary,
        key_facts=state.facts,
        sources=state.sources,
        partial_results=len(state.failed_queries) > 0,
        warnings=warnings,
    )
    
    return {"briefing": briefing}
