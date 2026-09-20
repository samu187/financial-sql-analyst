"""Download annual statements and store one stock at a time."""

import sqlite3
from pathlib import Path

import yfinance as yf
from platformdirs import user_data_path

data_dir = Path(user_data_path("financial-analyst", appauthor=False))
db_path = data_dir / "financial-data.sqlite"


def prepare_statement(statement):
    """Turn reporting-date columns into rows and metrics into columns."""
    frame = statement.T.copy()
    frame.index = frame.index.year
    frame.index.name = "year"
    return frame.reset_index().sort_values("year")


def download_financials(ticker: str) -> str:
    """Replace all three statement tables; return the database path on success."""
    try:
        stock = yf.Ticker(ticker)
        statements = {
            "income_stmt": stock.income_stmt,
            "balance_sheet": stock.balance_sheet,
            "cashflow": stock.cashflow,
        }
        if any(frame.empty for frame in statements.values()):
            print(f"Could not download all three annual statements for {ticker}.")
            return ""

        # Prepare everything before replacing the existing stock's data.
        with sqlite3.connect(":memory:") as staging:
            for table, statement in statements.items():
                prepare_statement(statement).to_sql(table, staging, index=False)
            data_dir.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(db_path) as database:
                staging.backup(database)
        return str(db_path)
    except Exception as error:
        print(f"Could not save financial statements for {ticker}: {error}")
        return ""
