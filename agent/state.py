"""Agent state definition for LangGraph."""

from typing import Annotated

from pydantic import BaseModel, Field

from models.schemas import Briefing, CompanyFact, SearchQuery, SearchResult


def merge_lists(left: list, right: list) -> list:
    """Merge two lists, used for state updates."""
    return left + right


class AgentState(BaseModel):
    """State passed between LangGraph nodes."""
    
    # Input
    company_name_raw: str = Field(description="Original company name from user")
    company_name_interpreted: str = Field(default="", description="LLM-interpreted company name")
    disambiguation_note: str = Field(default="", description="Context added for search disambiguation")
    
    # Planner output
    search_queries: Annotated[list[SearchQuery], merge_lists] = Field(default_factory=list)
    planning_reasoning: str = Field(default="")
    
    # Researcher output
    search_results: Annotated[list[SearchResult], merge_lists] = Field(default_factory=list)
    facts: Annotated[list[CompanyFact], merge_lists] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    
    # Data sufficiency
    sufficient_data: bool = Field(default=True)
    insufficiency_reason: str = Field(default="")
    
    # Errors and warnings
    failed_queries: Annotated[list[str], merge_lists] = Field(default_factory=list)
    warnings: Annotated[list[str], merge_lists] = Field(default_factory=list)
    
    # Final output
    briefing: Briefing | None = Field(default=None)
