from pathlib import Path

from app.mcp_server import (
    get_sample_manufacturing_financial_schema,
    run_sample_manufacturing_financial_sql,
)


def test_mcp_schema_tool_returns_sample_financial_schema(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "sample_financials.sqlite"))

    result = get_sample_manufacturing_financial_schema()

    assert result["database"] == "Sample Manufacturing Co. financial statements"
    assert "income_statements" in result["schema"]
    assert "balance_sheets" in result["schema"]
    assert "cash_flow_statements" in result["schema"]


def test_mcp_sql_tool_executes_safe_read_query(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "sample_financials.sqlite"))

    result = run_sample_manufacturing_financial_sql(
        "SELECT year, revenue FROM income_statements ORDER BY year;"
    )

    assert result["sql_is_safe"] is True
    assert result["sql_validation_error"] == ""
    assert result["query_error"] == ""
    assert result["rows"][0] == {"year": 2020, "revenue": 820000.0}
    assert len(result["rows"]) == 5


def test_mcp_sql_tool_blocks_unsafe_query(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "sample_financials.sqlite"))

    result = run_sample_manufacturing_financial_sql("DROP TABLE income_statements;")

    assert result["sql_is_safe"] is False
    assert result["rows"] == []
    assert result["query_error"] == ""
