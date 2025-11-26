"""Pydantic models for structured data throughout the agent."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """A search query with reasoning."""
    query: str = Field(description="The search query string")
    reasoning: str = Field(description="Why this query is useful for research")
    priority: bool = Field(default=False, description="Whether this targets priority domains")


class SearchResult(BaseModel):
    """A single search result from Tavily."""
    title: str
    url: str
    snippet: str
    domain: str


class CompanyFact(BaseModel):
    """A single fact about the company with source."""
    category: Literal["overview", "funding", "products", "news", "leadership", "headcount"]
    fact: str
    source_url: str
    source_index: int = Field(description="Index for citation numbering (1-based)")


class PlannerOutput(BaseModel):
    """Structured output from the Planner node."""
    company_interpreted: str = Field(description="Interpreted/disambiguated company name")
    disambiguation_note: str = Field(description="Brief note on interpretation for search context")
    queries: list[SearchQuery] = Field(description="List of search queries to execute")
    reasoning: str = Field(description="Overall planning reasoning")


class ResearcherOutput(BaseModel):
    """Structured output from the Researcher node."""
    facts: list[CompanyFact] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list, description="Ordered list of unique source URLs")


class Briefing(BaseModel):
    """Final briefing output."""
    company_name: str
    executive_summary: str = Field(description="2-3 paragraphs with [N] citations")
    key_facts: list[CompanyFact]
    sources: list[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    partial_results: bool = False
    warnings: list[str] = Field(default_factory=list)
