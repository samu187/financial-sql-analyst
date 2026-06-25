from financial_analyst_langgraph.config import load_settings
from financial_analyst_langgraph.database import seed_sample_company
from financial_analyst_langgraph.graph import build_graph


def test_graph_inspects_database_schema():
    settings = load_settings()
    seed_sample_company(settings.database_path)

    graph = build_graph()
    result = graph.invoke(
        {
            "database_path": str(settings.database_path),
            "user_question": "What data is available?",
        }
    )

    assert "companies" in result["schema_summary"]
    assert "income_statements" in result["schema_summary"]
    assert "balance_sheets" in result["schema_summary"]
    assert "cash_flow_statements" in result["schema_summary"]
