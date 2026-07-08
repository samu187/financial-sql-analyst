# LangGraph Financial Analyst

A full-stack financial analysis assistant that uses LangGraph, OpenAI, FastAPI, React, and SQLite to answer natural-language questions about company financial statements.

The app converts a user's finance question into a safe read-only SQL query, runs it against a sample financial database, and explains the result in plain English.

## Features

- Natural-language financial analysis over SQLite data
- LangGraph workflow with explicit analysis steps
- OpenAI-powered question classification, SQL generation, and answer writing
- Read-only SQL validation before execution
- SQLite sample database with five years of financial statements
- FastAPI backend serving both API routes and the built React frontend
- One-command app startup with `uv run start`
- React interface showing the answer, generated SQL, query result, and safety metadata

## Example Questions

```text
Show revenue growth over the last five years.
What's the coefficient of variation of revenues and the average annual increase?
Compare net income and free cash flow from 2020 to 2024.
What is the current ratio for each year?
```

## Tech Stack

- Python
- LangGraph
- LangChain
- OpenAI API
- FastAPI
- SQLite
- React
- Vite
- uv

## Architecture

```text
React frontend
    |
    v
FastAPI /api/analyze
    |
    v
LangGraph workflow
    |
    +--> inspect_schema
    +--> classify_question
    +--> generate_sql
    +--> validate_sql
    +--> execute_sql
    +--> write_final_answer
    |
    v
SQLite financial statements database
```

The graph returns a structured response containing the final answer, generated SQL, query result rows, SQL safety status, and relevant tables.

Each analysis request also writes a local debug trace to:

```text
log.json
```

The log includes every LangGraph node start/end event, structured OpenAI outputs, generated SQL, SQL execution row counts, query errors, and the final graph state.

## Data Model

The sample SQLite database contains five years of annual financial statement data for a fictional company.

Tables:

- `companies`
- `income_statements`
- `balance_sheets`
- `cash_flow_statements`

Cash flow conventions:

```text
change_in_cash = operating_cash_flow + investing_cash_flow + financing_cash_flow
free_cash_flow = operating_cash_flow + capex
```

`capex` is stored as a negative cash outflow.

## Project Structure

```text
.
├── data/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   └── seed_sample_data.py
├── app/
│   ├── config.py
│   ├── database.py
│   ├── graph.py
│   ├── main.py
│   ├── run_logger.py
│   └── static/
├── tests/
├── .env.example
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

Install `uv` if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install dependencies:

```bash
uv sync --extra dev
```

Create a local environment file:

```bash
cp .env.example .env
```

Add your OpenAI API key to `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

## Run The App

Start the FastAPI server and React frontend:

```bash
uv run start
```

Open:

```text
http://127.0.0.1:8000
```

The app uses the bundled sample company data and creates the local SQLite database at:

```text
data/sample_financials.sqlite
```

## API

Analyze a question:

```http
POST /api/analyze
```

Example request:

```json
{
  "question": "Show revenue growth over the last five years.",
  "data_source": "sample"
}
```

Health check:

```http
GET /api/health
```

## Development

Run tests:

```bash
uv run --extra dev pytest
```

If your local uv environment has a stale editable install after moving files around during development, run:

```bash
uv run --no-editable start
```

Seed the sample database manually:

```bash
uv run python scripts/seed_sample_data.py
```

Rebuild the frontend after editing React files:

```bash
cd frontend
npm install
npm run build
```

Then restart the app:

```bash
uv run start
```

## Notes

Ticker import via Alpha Vantage is included as a future extension point, but the current app uses bundled sample financial data so it can run immediately after setup.
