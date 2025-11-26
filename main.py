#!/usr/bin/env python3
"""
Company Research Agent - CLI Entrypoint

A LangGraph-based agent that researches companies and generates executive briefings.

Usage:
    python main.py "Company Name"
    python main.py "Stripe"
    python main.py "OpenAI"
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv


def main():
    """Main entry point for the company research agent."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Research a company and generate an executive briefing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py "Stripe"
    python main.py "OpenAI"
    python main.py "Anthropic"
        """
    )
    parser.add_argument(
        "company",
        type=str,
        help="Name of the company to research"
    )
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Validate environment
    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set. Please check your .env file.")
        sys.exit(1)
    if not os.getenv("TAVILY_API_KEY"):
        print("Error: TAVILY_API_KEY not set. Please check your .env file.")
        sys.exit(1)
    
    # Import after dotenv load to ensure env vars are available
    from agent.graph import run_research
    from utils.output import print_insufficient_data, print_preview, print_success, save_briefing
    
    try:
        # Run research
        final_state = run_research(args.company)
        
        # Handle results
        if final_state.briefing:
            if not final_state.sufficient_data:
                print_insufficient_data(final_state.insufficiency_reason)
            
            # Save briefing
            filepath = save_briefing(final_state.briefing)
            print_success(filepath)
            
            # Show preview
            print_preview(final_state.briefing.executive_summary)
        else:
            print("\n❌ Failed to generate briefing.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nResearch cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
