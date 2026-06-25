"""LangGraph workflow for the financial analyst assistant."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, StateGraph

from financial_analyst_langgraph.database import get_schema_summary


class AnalystState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes.

    LangGraph nodes receive the current state and return the fields they want to
    add or update. This keeps each step small and easy to test.
    """

    database_path: str
    user_question: str
    schema_summary: str


def inspect_schema(state: AnalystState) -> AnalystState:
    """Read the SQLite schema and store it in the graph state."""

    database_path = Path(state["database_path"])
    return {"schema_summary": get_schema_summary(database_path)}


def build_graph():
    """Build and compile the first version of the LangGraph workflow."""

    graph = StateGraph(AnalystState)

    graph.add_node("inspect_schema", inspect_schema)
    graph.set_entry_point("inspect_schema")
    graph.add_edge("inspect_schema", END)

    return graph.compile()
