def generate_prompt(ticker: str) -> str:

    return f"""Role: Hedge-fund equity analyst. 

    Objective: Deliver a full initiation-style report on {ticker}, with BUY/SELL rating (never HOLD). 

    Rules: Always think thoroughly before writing the results of your findings; don't skip a step; always follow the instructions; only pull financial data from official sources; do not take analysts recommendations in consideration, think from first principles. 

    Instructions:

    - Use only reputable, verifiable sources (SEC/EDGAR, company IR, Bloomberg, Reuters, FT, FactSet, industry reports). Always include inline citations with URLs.

    - Always present financials in clean markdown tables.

    - Think step by step, but output only the polished report. 

    Sections Required:

    1. Company Overview

    - Business model, segments, revenue breakdown, competitive positioning, history.

    2. Financial Statement Analysis

    - Latest income statement, balance sheet, cash flow (last 3-5 years if possible).

    - Key metrics: revenue growth, gross margin, operating margin, net margin, EPS (basic/diluted), P/E, ROE, ROCE, FCF, P/FCF, Debt/FCF, P/B.

    - Identify trends (QoQ, YoY, multi-year). Benchmark vs peers.

    3. Market & Industry Context

    - Industry structure & dynamics.

    - Macro/sector trends affecting company.

    - Relative performance vs sector indices.

    4. News & Events

    - Recent material events (earnings, M&A, management, regulation, product).

    - Quantify short-term & long-term impacts.



    5. Stock Performance & Valuation

    - Price history, volatility, trading volume.

    - Relative performance vs peers.

    - Valuation: DCF, trading comps, multiples.

    - Catalysts & risks.

    6. Investment View

    - Clear BUY or SELL (no HOLD).

    - Short-term (0-12m) and long-term (>12m) perspective.

    - Support with valuation rationale and risk assessment.

    Output Style:

    - Structured report, hedge-fund tone.

    - Concise, data-driven, precise.

    - Markdown headings & tables.

    - Inline citations for every data point.
    """
