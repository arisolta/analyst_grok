# Analyst Grok

## Description

An equity analyst assistant powered by Grok, designed to generate comprehensive initiation-style reports on stocks based on user input.

## Installation

To install and set up the project, follow these steps:

```bash
# Clone the repository
git clone https://github.com/arisolta/analyst-grok

# Navigate to the project directory
cd analyst-grok

# Install dependencies using uv
uv sync
```

## Environment Setup

Create a `.env` file in the project root and add your XAI API key:

```bash
XAI_API_KEY=your_api_key_here
```

## Usage

Run the application:

```bash
uv run main.py
```

When prompted, enter a stock ticker symbol (e.g., AAPL) - be mindful to adjust for non-US stocks by adding the exchange (e.g., BP.L or SAP.DE). The application will generate a comprehensive equity analyst report and save it as a timestamped `.txt` file.

## Requirements

- Python >= 3.12
- XAI API key
