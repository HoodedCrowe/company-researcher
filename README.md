# Company Research Agent

An AI-powered agent that researches companies and generates executive briefings using LangGraph, Claude, and Tavily search.

## Features

- **Intelligent Planning**: Interprets company names and generates targeted search queries
- **Authoritative Sources**: Prioritizes results from Crunchbase, LinkedIn, Bloomberg, etc.
- **Structured Extraction**: Extracts facts across 6 categories (overview, funding, products, leadership, headcount, news)
- **Visible Reasoning**: Shows agent thinking process in terminal
- **Graceful Handling**: Manages API failures and sparse data elegantly

## Quick Start

### 1. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` with your keys:
- **Anthropic**: Get from [console.anthropic.com](https://console.anthropic.com/)
- **Tavily**: Get from [tavily.com](https://tavily.com/) (free tier: 1000 searches/month)

### 4. Run

```bash
python main.py "Stripe"
```

## Example Output

```
🤔 Planning research for: Stripe
   Interpreting: "Stripe" → Stripe (fintech/payments company)
   
   Reasoning: I'll search for company overview, funding, products, 
   leadership, and headcount from authoritative sources.
   
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

──────────────────────────────────────────────────
Preview:
Stripe is a leading financial technology company...
──────────────────────────────────────────────────
```

## Output

Briefings are saved to `output/<company>_briefing.md` with:
- Executive summary (2-3 paragraphs with citations)
- Key facts by category
- Numbered source references

## Project Structure

```
company_researcher/
├── main.py           # CLI entrypoint
├── config.py         # Configuration settings
├── agent/
│   ├── graph.py      # LangGraph workflow
│   ├── nodes.py      # Planner, Researcher, Synthesizer
│   └── state.py      # Agent state model
├── search/
│   └── tavily.py     # Tavily client with retry
├── models/
│   └── schemas.py    # Pydantic models
└── utils/
    └── output.py     # Terminal + markdown output
```

## Configuration

Edit `config.py` to adjust:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_SEARCH_QUERIES` | 5 | Max queries per research |
| `TAVILY_MAX_RESULTS_PER_QUERY` | 5 | Results per search |
| `MIN_TOTAL_RESULTS` | 3 | Minimum for sufficient data |
| `MIN_FACT_CATEGORIES` | 2 | Minimum categories needed |
| `RETRY_ATTEMPTS` | 1 | Retries on search failure |

## Requirements

- Python 3.11+
- Anthropic API key
- Tavily API key (free tier available)
