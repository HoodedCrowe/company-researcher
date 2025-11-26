"""Output utilities for terminal formatting and markdown generation."""

import re
from datetime import datetime
from pathlib import Path

from config import Config
from models.schemas import Briefing, CompanyFact


def print_header(text: str, emoji: str = "🔷") -> None:
    """Print a formatted header."""
    print(f"\n{emoji} {text}")


def print_reasoning(text: str, indent: int = 3) -> None:
    """Print reasoning text with indentation."""
    prefix = " " * indent
    for line in text.split("\n"):
        print(f"{prefix}{line}")


def print_query(index: int, query: str) -> None:
    """Print a planned query."""
    print(f"   → Query {index}: \"{query}\"")


def print_search_result(query: str, count: int, success: bool, retry: bool = False) -> None:
    """Print search result status."""
    if success:
        retry_note = " (retry successful)" if retry else ""
        print(f"   ✓ \"{query[:40]}{'...' if len(query) > 40 else ''}\": Found {count} results{retry_note}")
    else:
        print(f"   ✗ \"{query[:40]}{'...' if len(query) > 40 else ''}\": Failed")


def print_search_retry(query: str) -> None:
    """Print retry notice."""
    print(f"   ⚠ \"{query[:40]}{'...' if len(query) > 40 else ''}\": Failed (retrying...)")


def print_facts_summary(facts: list[CompanyFact]) -> None:
    """Print summary of extracted facts."""
    categories = set(f.category for f in facts)
    print(f"   Found {len(facts)} facts across {len(categories)} categories")


def print_insufficient_data(reason: str) -> None:
    """Print insufficient data warning."""
    print(f"\n⚠️  Insufficient data: {reason}")


def print_success(filepath: Path) -> None:
    """Print success message with file path."""
    print(f"\n✅ Briefing saved to: {filepath}")


def print_preview(text: str, max_lines: int = 5) -> None:
    """Print a preview of the briefing."""
    print("\n" + "─" * 50)
    print("Preview:")
    lines = text.split("\n")[:max_lines]
    for line in lines:
        print(line[:80] + ("..." if len(line) > 80 else ""))
    print("─" * 50)


def sanitize_filename(name: str) -> str:
    """Convert company name to safe filename."""
    # Remove/replace special characters
    safe = re.sub(r'[^\w\s-]', '', name.lower())
    safe = re.sub(r'[-\s]+', '_', safe).strip('_')
    return safe


def generate_markdown(briefing: Briefing) -> str:
    """Generate markdown content from briefing."""
    lines = [
        f"# Executive Briefing: {briefing.company_name}",
        "",
        f"*Generated: {briefing.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}*",
        "",
    ]
    
    # Warnings section if any
    if briefing.warnings:
        lines.append("## ⚠️ Notices")
        lines.append("")
        for warning in briefing.warnings:
            lines.append(f"- {warning}")
        lines.append("")
    
    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(briefing.executive_summary)
    lines.append("")
    
    # Key Facts by category
    lines.append("## Key Facts")
    lines.append("")
    
    categories_order = ["overview", "funding", "products", "leadership", "headcount", "news"]
    category_titles = {
        "overview": "Overview",
        "funding": "Funding & Valuation",
        "products": "Products & Services",
        "leadership": "Leadership",
        "headcount": "Headcount",
        "news": "Recent News",
    }
    
    facts_by_category: dict[str, list[CompanyFact]] = {}
    for fact in briefing.key_facts:
        if fact.category not in facts_by_category:
            facts_by_category[fact.category] = []
        facts_by_category[fact.category].append(fact)
    
    for category in categories_order:
        if category in facts_by_category:
            lines.append(f"**{category_titles.get(category, category.title())}**")
            lines.append("")
            for fact in facts_by_category[category]:
                lines.append(f"- {fact.fact} [{fact.source_index}]")
            lines.append("")
    
    # Sources
    lines.append("## Sources")
    lines.append("")
    for i, source in enumerate(briefing.sources, 1):
        lines.append(f"{i}. {source}")
    lines.append("")
    
    return "\n".join(lines)


def save_briefing(briefing: Briefing) -> Path:
    """Save briefing to markdown file and return path."""
    output_dir = Config.ensure_output_dir()
    filename = f"{sanitize_filename(briefing.company_name)}_briefing.md"
    filepath = output_dir / filename
    
    content = generate_markdown(briefing)
    filepath.write_text(content)
    
    return filepath
