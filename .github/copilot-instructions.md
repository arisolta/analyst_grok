# Analyst Grok - AI Coding Agent Instructions

## Project Overview

This is a Python CLI application that generates comprehensive equity analyst reports using Grok AI. Users input stock tickers, and the system produces detailed initiation-style reports with BUY/SELL recommendations.

## Architecture

- **main.py**: Entry point handling user input, API calls, and file output
- **prompt.py**: Contains `generate_prompt()` function with detailed analyst instructions
- **pyproject.toml**: Project configuration with dependencies (xai-sdk, python-dotenv)

## Key Patterns & Conventions

### API Integration

- Uses XAI SDK for Grok API calls with `grok-4-1-fast-reasoning` model
- Requires `XAI_API_KEY` environment variable (loaded via python-dotenv)
- Search enabled with `SearchParameters(mode="auto", max_search_results=10)`
- 3600s timeout for reasoning models

### Input/Output Handling

- User input: Stock ticker symbol (converted to uppercase)
- Output: Timestamped `.txt` files named `{TICKER}-{YYYY-MM-DD_HH-MM-SS}.txt`
- Reports use markdown formatting with tables, headings, and inline citations

### Report Structure

Reports follow hedge-fund analyst format with 6 required sections:

1. Company Overview (business model, segments, competition)
2. Financial Statement Analysis (3-5 year tables, key metrics)
3. Market & Industry Context (sector dynamics, macro trends)
4. News & Events (recent developments, impact analysis)
5. Stock Performance & Valuation (price history, DCF, comps)
6. Investment View (BUY/SELL rating with time horizons)

### Dependencies & Environment

- Python >=3.12 required
- Uses `uv` for package management (see uv.lock)
- Virtual environment in `.venv/` directory
- Run with: `uv run main.py`

### Development Workflow

- Install: `uv sync` (installs dependencies)
- Run: `uv run main.py`
- Environment setup: Copy `.env.example` to `.env` and add XAI_API_KEY

### Code Style Notes

- Simple, linear scripts with minimal error handling
- Date formatting: `YYYY-MM-DD` for today, `YYYY-MM-DD_HH-MM-SS` for timestamps
- Financial data presented in markdown tables with inline URL citations
- No testing framework currently implemented</content>
  <parameter name="filePath">/Users/arashsoltanieh/Desktop/Code/xai/analyst_grok/.github/copilot-instructions.md
