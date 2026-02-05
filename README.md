# Analyst Grok

## Description
An advanced, multi-agent equity analyst powered by Grok (xAI). This tool orchestrates a "Committee of Experts" to research, analyze, and write professional-grade initiation reports on public stocks.

## Architecture
The system uses a sequential multi-agent pipeline to ensure rigor and depth:

1.  **Data Scout**: Fetches real-time price, financial statements, and news via `yfinance`.
2.  **Competitor Benchmarker**: Automatically identifies and scouts key competitors for relative valuation.
3.  **Fundamental Analyst** (`grok-4-1-fast-reasoning`): Conducts deep-dive financial analysis and peer comparison.
4.  **Sentiment Analyst** (`grok-4-1-fast-non-reasoning`): performs **Deep Research** via web search to extract management tone, earnings guidance, and qualitative catalysts.
5.  **Portfolio Manager** (`grok-4-1-fast-reasoning`): Synthesizes all data to issue a Rating (BUY/SELL/HOLD), a specific Target Price, and a detailed Investment Thesis.
6.  **Editor** (`grok-4-1-fast-non-reasoning`): Polishes the final report into a structured Markdown document.

## Features
- **Committee of Experts**: Specialized agents handle different parts of the analysis to reduce hallucinations.
- **Relative Valuation**: Automatic peer identification and side-by-side metric comparison.
- **Management Tone Analysis**: Goes beyond headlines by searching for earnings call transcripts and executive commentary.
- **Technical Robustness**: 
  - Automatic retries on API errors using `tenacity`.
  - File-based caching for `yfinance` to prevent rate-limiting.
  - Comprehensive JSON metadata for every run (audit trail).

## Installation
```bash
# Clone the repository
git clone https://github.com/arisolta/analyst-grok
cd analyst-grok

# Install dependencies using uv
uv sync
```

## Environment Setup
Create a `.env` file in the project root:
```bash
XAI_API_KEY=your_api_key_here
```

## Usage
```bash
# Analyze a specific ticker
uv run main.py NVDA

# Run interactively
uv run main.py
```

## Output
Reports are saved in the `results/` directory:
- `TICKER-TIMESTAMP.md`: The professional markdown report.
- `TICKER-TIMESTAMP.json`: Full metadata, including intermediate agent thoughts and raw data snapshots.

## Requirements
- Python >= 3.12
- XAI API key (Grok-4 access)
