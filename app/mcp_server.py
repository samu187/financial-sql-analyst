"""MCP server for Sample Manufacturing financial statements."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from app.config import load_settings
from app.database import execute_read_query, get_schema_summary, seed_sample_company
from app.graph import validate_sql


mcp = FastMCP(
    "sample-manufacturing-financials",
    instructions=(
        "Use these tools to answer questions about Sample Manufacturing Co. "
        "financial statements. First inspect the schema, then run read-only SQLite "
        "queries against the local sample financials database."
    ),
)


@mcp.tool(
    name="get_sample_manufacturing_financial_schema",
    title="Get Sample Manufacturing Financial Schema",
    description=(
        "Use this tool when the user asks about Sample Manufacturing Co. financials. "
        "It returns the SQLite tables and columns available for the sample company's "
        "income statements, balance sheets, cash flow statements, and company metadata."
    ),
)
def get_sample_manufacturing_financial_schema() -> dict[str, str]:
    """Return the schema for the Sample Manufacturing financial database."""

    settings = load_settings()
    seed_sample_company(settings.database_path)

    return {
        "database": "Sample Manufacturing Co. financial statements",
        "schema": get_schema_summary(settings.database_path),
    }


@mcp.tool(
    name="run_sample_manufacturing_financial_sql",
    title="Run Sample Manufacturing Financial SQL",
    description=(
        "Use this tool to answer questions about Sample Manufacturing Co. financials "
        "after inspecting the schema. Provide one read-only SQLite SELECT or WITH query. "
        "The tool validates that the SQL is read-only before executing it and returns rows "
        "from the local sample financials database."
    ),
)
def run_sample_manufacturing_financial_sql(sql_query: str) -> dict[str, Any]:
    """Validate and execute one read-only SQL query against the sample database."""

    validation = validate_sql({"sql_query": sql_query})
    if not validation["sql_is_safe"]:
        return {
            "sql_query": sql_query,
            "sql_is_safe": False,
            "sql_validation_error": validation["sql_validation_error"],
            "rows": [],
            "query_error": "",
        }

    settings = load_settings()
    seed_sample_company(settings.database_path)

    try:
        rows = execute_read_query(settings.database_path, validation["sql_query"])
    except Exception as error:
        return {
            "sql_query": validation["sql_query"],
            "sql_is_safe": True,
            "sql_validation_error": "",
            "rows": [],
            "query_error": str(error),
        }

    return {
        "sql_query": validation["sql_query"],
        "sql_is_safe": True,
        "sql_validation_error": "",
        "rows": rows,
        "query_error": "",
    }


def start() -> None:
    """Run the MCP server over stdio."""

    mcp.run(transport="stdio")


if __name__ == "__main__":
    start()
