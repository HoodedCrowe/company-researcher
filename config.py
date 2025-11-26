"""Configuration settings for the company research agent."""

from pathlib import Path


class Config:
    """Central configuration for the research agent."""
    
    # Search settings
    MAX_SEARCH_QUERIES: int = 5
    TAVILY_MAX_RESULTS_PER_QUERY: int = 5
    RETRY_ATTEMPTS: int = 1
    
    # Data sufficiency thresholds
    MIN_TOTAL_RESULTS: int = 3
    MIN_FACT_CATEGORIES: int = 2
    
    # Priority domains - searched first to quickly determine data availability
    PRIORITY_DOMAINS: list[str] = [
        "crunchbase.com",
        "linkedin.com",
        "bloomberg.com",
        "reuters.com",
        "techcrunch.com",
        "forbes.com",
        "wsj.com",
    ]
    
    # Output settings
    OUTPUT_DIR: Path = Path("output")
    
    # Model settings
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    
    @classmethod
    def ensure_output_dir(cls) -> Path:
        """Ensure output directory exists and return path."""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        return cls.OUTPUT_DIR
