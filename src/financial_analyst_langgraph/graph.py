"""LangGraph workflow for the financial analyst assistant."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from financial_analyst_langgraph.database import execute_read_query, get_schema_summary


QuestionIntent = Literal["metric", "trend", "table", "explanation", "unknown"]
ResponseFormat = Literal["answer", "table", "bar_chart", "line_chart"]


class AnalystState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes.

    LangGraph nodes receive the current state and return the fields they want to
    add or update. This keeps each step small and easy to test.
    """

    database_path: str
    user_question: str
    schema_summary: str
    question_intent: QuestionIntent
    response_format: ResponseFormat
    relevant_tables: list[str]
    classification_reasoning: str
    sql_query: str
    sql_reasoning: str
    sql_is_safe: bool
    sql_validation_error: str
    query_result: list[dict[str, Any]]
    final_answer: str


class QuestionClassification(BaseModel):
    """Structured output returned by the OpenAI classification call."""

    intent: QuestionIntent = Field(
        description="The type of financial analysis the user is asking for."
    )
    response_format: ResponseFormat = Field(
        description="The best response format for the user's question."
    )
    relevant_tables: list[str] = Field(
        description="Database tables likely needed to answer the question."
    )
    reasoning: str = Field(
        description="A concise explanation of why this classification was chosen."
    )


class SQLGeneration(BaseModel):
    """Structured output returned by the SQL generation call."""

    sql_query: str = Field(
        description="One SQLite SELECT query that answers the user's question."
    )
    reasoning: str = Field(
        description="A concise explanation of why this query answers the question."
    )


def inspect_schema(state: AnalystState) -> AnalystState:
    """Read the SQLite schema and store it in the graph state."""

    database_path = Path(state["database_path"])
    return {"schema_summary": get_schema_summary(database_path)}


def classify_question(state: AnalystState, llm: ChatOpenAI) -> AnalystState:
    """Use OpenAI to classify the user's finance question."""

    structured_llm = llm.with_structured_output(QuestionClassification)
    classification = structured_llm.invoke(
        [
            (
                "system",
                "You classify financial analysis questions for a SQLite-backed "
                "LangGraph assistant. Use only the provided schema. Do not write SQL yet.",
            ),
            (
                "human",
                f"""
Question:
{state["user_question"]}

Database schema:
{state["schema_summary"]}

Classify the question by intent, best response format, and relevant tables.
""".strip(),
            ),
        ]
    )

    return {
        "question_intent": classification.intent,
        "response_format": classification.response_format,
        "relevant_tables": classification.relevant_tables,
        "classification_reasoning": classification.reasoning,
    }


def generate_sql(state: AnalystState, llm: ChatOpenAI) -> AnalystState:
    """Use OpenAI to generate a read-only SQLite query."""

    structured_llm = llm.with_structured_output(SQLGeneration)
    sql_generation = structured_llm.invoke(
        [
            (
                "system",
                "You write safe, read-only SQLite SELECT queries for a financial "
                "analysis assistant. Return exactly one query. Do not use INSERT, "
                "UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, or multiple statements.",
            ),
            (
                "human",
                f"""
Question:
{state["user_question"]}

Question intent:
{state["question_intent"]}

Relevant tables:
{", ".join(state["relevant_tables"])}

Database schema:
{state["schema_summary"]}

Write one SQLite query that returns the data needed to answer the question.
Prefer clear column aliases. Include ORDER BY year when showing multi-year trends.
""".strip(),
            ),
        ]
    )

    return {
        "sql_query": sql_generation.sql_query.strip(),
        "sql_reasoning": sql_generation.reasoning,
    }


def validate_sql(state: AnalystState) -> AnalystState:
    """Validate that the generated SQL is a single read-only query."""

    sql_query = state["sql_query"].strip().rstrip(";")
    normalized_query = re.sub(r"\s+", " ", sql_query).strip().lower()

    if not normalized_query:
        return {
            "sql_is_safe": False,
            "sql_validation_error": "The generated SQL query was empty.",
        }

    if ";" in normalized_query:
        return {
            "sql_is_safe": False,
            "sql_validation_error": "Only one SQL statement is allowed.",
        }

    if not normalized_query.startswith(("select ", "with ")):
        return {
            "sql_is_safe": False,
            "sql_validation_error": "Only read-only SELECT queries are allowed.",
        }

    forbidden_words = (
        "alter",
        "attach",
        "create",
        "delete",
        "detach",
        "drop",
        "insert",
        "pragma",
        "replace",
        "update",
        "vacuum",
    )
    forbidden_pattern = r"\b(" + "|".join(forbidden_words) + r")\b"
    if re.search(forbidden_pattern, normalized_query):
        return {
            "sql_is_safe": False,
            "sql_validation_error": "The query contains a forbidden write/admin operation.",
        }

    return {"sql_query": sql_query, "sql_is_safe": True, "sql_validation_error": ""}


def execute_sql(state: AnalystState) -> AnalystState:
    """Run the validated SQL query against SQLite."""

    if not state["sql_is_safe"]:
        return {"query_result": []}

    database_path = Path(state["database_path"])
    return {"query_result": execute_read_query(database_path, state["sql_query"])}


def write_final_answer(state: AnalystState, llm: ChatOpenAI) -> AnalystState:
    """Use OpenAI to explain the query result in plain English."""

    if not state["sql_is_safe"]:
        return {
            "final_answer": (
                "I did not run the SQL query because it failed the read-only safety check: "
                f"{state['sql_validation_error']}"
            )
        }

    response = llm.invoke(
        [
            (
                "system",
                "You are a careful financial analyst. Explain findings from SQLite query "
                "results in concise plain English. Do not invent data. If the query result "
                "is empty, say that the database did not return matching rows.",
            ),
            (
                "human",
                f"""
User question:
{state["user_question"]}

SQL query that was run:
{state["sql_query"]}

SQL reasoning:
{state["sql_reasoning"]}

Query result:
{state["query_result"]}

Write the final answer. Mention important numbers and years. Keep it brief.
""".strip(),
            ),
        ]
    )

    return {"final_answer": response.content}


def route_after_validation(state: AnalystState) -> str:
    """Decide whether to execute SQL or skip straight to the final answer."""

    if state["sql_is_safe"]:
        return "execute_sql"
    return "write_final_answer"


def build_graph(openai_api_key: str, openai_model: str):
    """Build and compile the first version of the LangGraph workflow."""

    llm = ChatOpenAI(api_key=openai_api_key, model=openai_model)
    graph = StateGraph(AnalystState)

    graph.add_node("inspect_schema", inspect_schema)
    graph.add_node("classify_question", lambda state: classify_question(state, llm))
    graph.add_node("generate_sql", lambda state: generate_sql(state, llm))
    graph.add_node("validate_sql", validate_sql)
    graph.add_node("execute_sql", execute_sql)
    graph.add_node("write_final_answer", lambda state: write_final_answer(state, llm))

    graph.set_entry_point("inspect_schema")
    graph.add_edge("inspect_schema", "classify_question")
    graph.add_edge("classify_question", "generate_sql")
    graph.add_edge("generate_sql", "validate_sql")
    graph.add_conditional_edges(
        "validate_sql",
        route_after_validation,
        {
            "execute_sql": "execute_sql",
            "write_final_answer": "write_final_answer",
        },
    )
    graph.add_edge("execute_sql", "write_final_answer")
    graph.add_edge("write_final_answer", END)

    return graph.compile()
