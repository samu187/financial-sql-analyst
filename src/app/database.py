"""SQLite database setup and sample data loading."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    currency TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS income_statements (
    id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    revenue REAL NOT NULL,
    cost_of_revenue REAL NOT NULL,
    gross_profit REAL NOT NULL,
    operating_expenses REAL NOT NULL,
    ebitda REAL NOT NULL,
    depreciation_amortization REAL NOT NULL,
    ebit REAL NOT NULL,
    interest_expense REAL NOT NULL,
    ebt REAL NOT NULL,
    income_tax_expense REAL NOT NULL,
    net_income REAL NOT NULL,
    UNIQUE(company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS balance_sheets (
    id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    cash_and_equivalents REAL NOT NULL,
    accounts_receivable REAL NOT NULL,
    inventory REAL NOT NULL,
    current_assets REAL NOT NULL,
    property_plant_equipment REAL NOT NULL,
    total_assets REAL NOT NULL,
    accounts_payable REAL NOT NULL,
    short_term_debt REAL NOT NULL,
    current_liabilities REAL NOT NULL,
    long_term_debt REAL NOT NULL,
    total_liabilities REAL NOT NULL,
    shareholders_equity REAL NOT NULL,
    UNIQUE(company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cash_flow_statements (
    id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    net_income REAL NOT NULL,
    depreciation_amortization REAL NOT NULL,
    change_in_working_capital REAL NOT NULL,
    operating_cash_flow REAL NOT NULL,
    capex REAL NOT NULL,
    investing_cash_flow REAL NOT NULL,
    financing_cash_flow REAL NOT NULL,
    change_in_cash REAL NOT NULL,
    free_cash_flow REAL NOT NULL,
    UNIQUE(company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);
"""


SAMPLE_COMPANY = {
    "ticker": "SAMPLE",
    "name": "Sample Manufacturing Co.",
    "currency": "USD",
}


SAMPLE_INCOME_STATEMENTS = [
    {
        "year": 2020,
        "revenue": 820_000,
        "cost_of_revenue": 475_600,
        "gross_profit": 344_400,
        "operating_expenses": 210_000,
        "ebitda": 134_400,
        "depreciation_amortization": 38_000,
        "ebit": 96_400,
        "interest_expense": 15_000,
        "ebt": 81_400,
        "income_tax_expense": 17_094,
        "net_income": 64_306,
    },
    {
        "year": 2021,
        "revenue": 910_000,
        "cost_of_revenue": 509_600,
        "gross_profit": 400_400,
        "operating_expenses": 232_000,
        "ebitda": 168_400,
        "depreciation_amortization": 42_000,
        "ebit": 126_400,
        "interest_expense": 16_500,
        "ebt": 109_900,
        "income_tax_expense": 23_079,
        "net_income": 86_821,
    },
    {
        "year": 2022,
        "revenue": 1_035_000,
        "cost_of_revenue": 569_250,
        "gross_profit": 465_750,
        "operating_expenses": 258_000,
        "ebitda": 207_750,
        "depreciation_amortization": 47_000,
        "ebit": 160_750,
        "interest_expense": 18_000,
        "ebt": 142_750,
        "income_tax_expense": 29_978,
        "net_income": 112_772,
    },
    {
        "year": 2023,
        "revenue": 1_185_000,
        "cost_of_revenue": 628_050,
        "gross_profit": 556_950,
        "operating_expenses": 292_000,
        "ebitda": 264_950,
        "depreciation_amortization": 54_000,
        "ebit": 210_950,
        "interest_expense": 19_000,
        "ebt": 191_950,
        "income_tax_expense": 40_310,
        "net_income": 151_640,
    },
    {
        "year": 2024,
        "revenue": 1_340_000,
        "cost_of_revenue": 696_800,
        "gross_profit": 643_200,
        "operating_expenses": 326_000,
        "ebitda": 317_200,
        "depreciation_amortization": 61_000,
        "ebit": 256_200,
        "interest_expense": 20_500,
        "ebt": 235_700,
        "income_tax_expense": 49_497,
        "net_income": 186_203,
    },
]


SAMPLE_BALANCE_SHEETS = [
    {
        "year": 2020,
        "cash_and_equivalents": 72_000,
        "accounts_receivable": 88_000,
        "inventory": 112_000,
        "current_assets": 292_000,
        "property_plant_equipment": 420_000,
        "total_assets": 760_000,
        "accounts_payable": 74_000,
        "short_term_debt": 42_000,
        "current_liabilities": 156_000,
        "long_term_debt": 210_000,
        "total_liabilities": 402_000,
        "shareholders_equity": 358_000,
    },
    {
        "year": 2021,
        "cash_and_equivalents": 81_000,
        "accounts_receivable": 96_000,
        "inventory": 125_000,
        "current_assets": 326_000,
        "property_plant_equipment": 455_000,
        "total_assets": 832_000,
        "accounts_payable": 79_000,
        "short_term_debt": 45_000,
        "current_liabilities": 166_000,
        "long_term_debt": 226_000,
        "total_liabilities": 430_000,
        "shareholders_equity": 402_000,
    },
    {
        "year": 2022,
        "cash_and_equivalents": 94_000,
        "accounts_receivable": 110_000,
        "inventory": 139_000,
        "current_assets": 370_000,
        "property_plant_equipment": 508_000,
        "total_assets": 936_000,
        "accounts_payable": 87_000,
        "short_term_debt": 48_000,
        "current_liabilities": 181_000,
        "long_term_debt": 246_000,
        "total_liabilities": 468_000,
        "shareholders_equity": 468_000,
    },
    {
        "year": 2023,
        "cash_and_equivalents": 118_000,
        "accounts_receivable": 127_000,
        "inventory": 151_000,
        "current_assets": 427_000,
        "property_plant_equipment": 566_000,
        "total_assets": 1_058_000,
        "accounts_payable": 95_000,
        "short_term_debt": 52_000,
        "current_liabilities": 194_000,
        "long_term_debt": 258_000,
        "total_liabilities": 492_000,
        "shareholders_equity": 566_000,
    },
    {
        "year": 2024,
        "cash_and_equivalents": 151_000,
        "accounts_receivable": 139_000,
        "inventory": 164_000,
        "current_assets": 490_000,
        "property_plant_equipment": 628_000,
        "total_assets": 1_192_000,
        "accounts_payable": 104_000,
        "short_term_debt": 55_000,
        "current_liabilities": 207_000,
        "long_term_debt": 264_000,
        "total_liabilities": 516_000,
        "shareholders_equity": 676_000,
    },
]


SAMPLE_CASH_FLOW_STATEMENTS = [
    {
        "year": 2020,
        "net_income": 64_306,
        "depreciation_amortization": 38_000,
        "change_in_working_capital": -11_000,
        "operating_cash_flow": 91_306,
        "capex": -62_000,
        "investing_cash_flow": -68_000,
        "financing_cash_flow": -14_000,
        "change_in_cash": 9_306,
        "free_cash_flow": 29_306,
    },
    {
        "year": 2021,
        "net_income": 86_821,
        "depreciation_amortization": 42_000,
        "change_in_working_capital": -14_000,
        "operating_cash_flow": 114_821,
        "capex": -77_000,
        "investing_cash_flow": -84_000,
        "financing_cash_flow": -22_000,
        "change_in_cash": 8_821,
        "free_cash_flow": 37_821,
    },
    {
        "year": 2022,
        "net_income": 112_772,
        "depreciation_amortization": 47_000,
        "change_in_working_capital": -18_000,
        "operating_cash_flow": 141_772,
        "capex": -91_000,
        "investing_cash_flow": -99_000,
        "financing_cash_flow": -30_000,
        "change_in_cash": 12_772,
        "free_cash_flow": 50_772,
    },
    {
        "year": 2023,
        "net_income": 151_640,
        "depreciation_amortization": 54_000,
        "change_in_working_capital": -22_000,
        "operating_cash_flow": 183_640,
        "capex": -108_000,
        "investing_cash_flow": -117_000,
        "financing_cash_flow": -43_000,
        "change_in_cash": 23_640,
        "free_cash_flow": 75_640,
    },
    {
        "year": 2024,
        "net_income": 186_203,
        "depreciation_amortization": 61_000,
        "change_in_working_capital": -25_000,
        "operating_cash_flow": 222_203,
        "capex": -124_000,
        "investing_cash_flow": -134_000,
        "financing_cash_flow": -55_000,
        "change_in_cash": 33_203,
        "free_cash_flow": 98_203,
    },
]


def connect(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with foreign keys enabled."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def initialize_database(database_path: Path) -> None:
    """Create the database schema if it does not already exist."""

    with connect(database_path) as connection:
        connection.executescript(SCHEMA_SQL)


def seed_sample_company(database_path: Path) -> int:
    """Insert or refresh the bundled sample company and its statements."""

    initialize_database(database_path)

    with connect(database_path) as connection:
        company_id = _upsert_sample_company(connection)

        _replace_statement_rows(
            connection,
            table_name="income_statements",
            company_id=company_id,
            rows=SAMPLE_INCOME_STATEMENTS,
        )
        _replace_statement_rows(
            connection,
            table_name="balance_sheets",
            company_id=company_id,
            rows=SAMPLE_BALANCE_SHEETS,
        )
        _replace_statement_rows(
            connection,
            table_name="cash_flow_statements",
            company_id=company_id,
            rows=SAMPLE_CASH_FLOW_STATEMENTS,
        )

        return company_id


def get_schema_summary(database_path: Path) -> str:
    """Return a human-readable summary of the database tables and columns."""

    with connect(database_path) as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
            """
        ).fetchall()

        summary_lines: list[str] = []
        for table in tables:
            table_name = table["name"]
            columns = connection.execute(f"PRAGMA table_info({table_name});").fetchall()
            column_names = ", ".join(column["name"] for column in columns)
            summary_lines.append(f"- {table_name}: {column_names}")

        return "\n".join(summary_lines)


def execute_read_query(database_path: Path, sql_query: str) -> list[dict[str, Any]]:
    """Execute a read-only SQL query and return rows as dictionaries."""

    with connect(database_path) as connection:
        rows = connection.execute(sql_query).fetchall()
        return [dict(row) for row in rows]


def _upsert_sample_company(connection: sqlite3.Connection) -> int:
    connection.execute(
        """
        INSERT INTO companies (ticker, name, currency)
        VALUES (:ticker, :name, :currency)
        ON CONFLICT(ticker) DO UPDATE SET
            name = excluded.name,
            currency = excluded.currency;
        """,
        SAMPLE_COMPANY,
    )

    row = connection.execute(
        "SELECT id FROM companies WHERE ticker = ?;",
        (SAMPLE_COMPANY["ticker"],),
    ).fetchone()
    if row is None:
        raise RuntimeError("Sample company was not created.")

    return int(row["id"])


def _replace_statement_rows(
    connection: sqlite3.Connection,
    table_name: str,
    company_id: int,
    rows: list[dict[str, float | int]],
) -> None:
    connection.execute(f"DELETE FROM {table_name} WHERE company_id = ?;", (company_id,))

    for row in rows:
        payload = {"company_id": company_id, **row}
        columns = ", ".join(payload)
        placeholders = ", ".join(f":{column}" for column in payload)
        connection.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});",
            payload,
        )
