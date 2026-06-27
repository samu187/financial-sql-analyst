from pathlib import Path

from financial_analyst_langgraph.database import execute_read_query, get_schema_summary, seed_sample_company
from financial_analyst_langgraph.graph import execute_sql, inspect_schema, validate_sql


def test_inspect_schema_node_reads_database_schema(tmp_path: Path):
    database_path = tmp_path / "sample_financials.sqlite"
    seed_sample_company(database_path)

    result = inspect_schema({"database_path": str(database_path)})

    assert "companies" in result["schema_summary"]
    assert "income_statements" in result["schema_summary"]
    assert "balance_sheets" in result["schema_summary"]
    assert "cash_flow_statements" in result["schema_summary"]


def test_schema_summary_reads_seeded_database(tmp_path: Path):
    database_path = tmp_path / "sample_financials.sqlite"
    seed_sample_company(database_path)

    schema_summary = get_schema_summary(database_path)

    assert "income_statements" in schema_summary


def test_validate_sql_accepts_single_select_statement():
    result = validate_sql(
        {"sql_query": "SELECT year, revenue FROM income_statements ORDER BY year;"}
    )

    assert result["sql_is_safe"] is True
    assert result["sql_query"] == "SELECT year, revenue FROM income_statements ORDER BY year"


def test_validate_sql_rejects_write_statement():
    result = validate_sql({"sql_query": "DROP TABLE companies;"})

    assert result["sql_is_safe"] is False


def test_execute_sql_returns_rows_from_seeded_database(tmp_path: Path):
    database_path = tmp_path / "sample_financials.sqlite"
    seed_sample_company(database_path)

    validation_result = validate_sql(
        {
            "sql_query": (
                "SELECT year, revenue "
                "FROM income_statements "
                "ORDER BY year"
            )
        }
    )
    result = execute_sql(
        {
            "database_path": str(database_path),
            "sql_query": validation_result["sql_query"],
            "sql_is_safe": validation_result["sql_is_safe"],
        }
    )

    assert result["query_result"][0] == {"year": 2020, "revenue": 820000.0}
    assert len(result["query_result"]) == 5


def test_execute_read_query_returns_dict_rows(tmp_path: Path):
    database_path = tmp_path / "sample_financials.sqlite"
    seed_sample_company(database_path)

    rows = execute_read_query(database_path, "SELECT ticker, name FROM companies")

    assert rows == [{"ticker": "SAMPLE", "name": "Sample Manufacturing Co."}]
