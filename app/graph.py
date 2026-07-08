"""LangGraph workflow for the financial analyst assistant."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from app.database import execute_read_query, get_schema_summary
from app.run_logger import RunLogger


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
    query_error: str
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


def inspect_schema(state: AnalystState, logger: RunLogger | None = None) -> AnalystState:
    """Read the SQLite schema and store it in the graph state."""

    if logger:
        logger.node_start("inspect_schema", state)

    database_path = Path(state["database_path"])
    output = {"schema_summary": get_schema_summary(database_path)}

    if logger:
        logger.node_end("inspect_schema", output)

    return output


def classify_question(
    state: AnalystState,
    llm: ChatOpenAI,
    logger: RunLogger | None = None,
) -> AnalystState:
    """Use OpenAI to classify the user's finance question."""

    if logger:
        logger.node_start("classify_question", state)

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

    if logger:
        logger.llm_result("classify_question", classification)

    output = {
        "question_intent": classification.intent,
        "response_format": classification.response_format,
        "relevant_tables": classification.relevant_tables,
        "classification_reasoning": classification.reasoning,
    }

    if logger:
        logger.node_end("classify_question", output)

    return output


def generate_sql(
    state: AnalystState,
    llm: ChatOpenAI,
    logger: RunLogger | None = None,
) -> AnalystState:
    """Use OpenAI to generate a read-only SQLite query."""

    if logger:
        logger.node_start("generate_sql", state)

    structured_llm = llm.with_structured_output(SQLGeneration)
    sql_generation = structured_llm.invoke(
        [
            (
                "system",
                "You write safe, read-only SQLite SELECT queries for a financial "
                "analysis assistant. Return exactly one query. Do not use INSERT, "
                "UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, or multiple statements. "
                "Use SQLite-supported functions only. SQLite does not support "
                "STDDEV, STDDEV_POP, STDDEV_SAMP, VARIANCE, or PERCENTILE functions. "
                "For coefficient of variation, calculate standard deviation manually "
                "as sqrt(avg(x * x) - avg(x) * avg(x)), then divide by avg(x).",
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

    if logger:
        logger.llm_result("generate_sql", sql_generation)

    output = {
        "sql_query": sql_generation.sql_query.strip(),
        "sql_reasoning": sql_generation.reasoning,
    }

    if logger:
        logger.node_end("generate_sql", output)

    return output


def validate_sql(state: AnalystState, logger: RunLogger | None = None) -> AnalystState:
    """Validate that the generated SQL is a single read-only query."""

    if logger:
        logger.node_start("validate_sql", state)

    sql_query = state["sql_query"].strip().rstrip(";")
    normalized_query = re.sub(r"\s+", " ", sql_query).strip().lower()

    output: AnalystState
    if not normalized_query:
        output = {
            "sql_is_safe": False,
            "sql_validation_error": "The generated SQL query was empty.",
        }
        if logger:
            logger.node_end("validate_sql", output)
        return output

    if ";" in normalized_query:
        output = {
            "sql_is_safe": False,
            "sql_validation_error": "Only one SQL statement is allowed.",
        }
        if logger:
            logger.node_end("validate_sql", output)
        return output

    if not normalized_query.startswith(("select ", "with ")):
        output = {
            "sql_is_safe": False,
            "sql_validation_error": "Only read-only SELECT queries are allowed.",
        }
        if logger:
            logger.node_end("validate_sql", output)
        return output

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
        output = {
            "sql_is_safe": False,
            "sql_validation_error": "The query contains a forbidden write/admin operation.",
        }
        if logger:
            logger.node_end("validate_sql", output)
        return output

    unsupported_functions = (
        "stddev",
        "stddev_pop",
        "stddev_samp",
        "variance",
        "percentile",
    )
    unsupported_pattern = r"\b(" + "|".join(unsupported_functions) + r")\s*\("
    if re.search(unsupported_pattern, normalized_query):
        output = {
            "sql_is_safe": False,
            "sql_validation_error": (
                "The query uses a statistical function that SQLite does not provide. "
                "Use SQLite arithmetic such as sqrt(avg(x * x) - avg(x) * avg(x)) instead."
            ),
        }
        if logger:
            logger.node_end("validate_sql", output)
        return output

    output = {"sql_query": sql_query, "sql_is_safe": True, "sql_validation_error": ""}
    if logger:
        logger.node_end("validate_sql", output)
    return output


def execute_sql(state: AnalystState, logger: RunLogger | None = None) -> AnalystState:
    """Run the validated SQL query against SQLite."""

    if logger:
        logger.node_start("execute_sql", state)

    if not state["sql_is_safe"]:
        output = {"query_result": [], "query_error": ""}
        if logger:
            logger.node_end("execute_sql", output)
        return output

    database_path = Path(state["database_path"])
    try:
        query_result = execute_read_query(database_path, state["sql_query"])
        output = {
            "query_result": query_result,
            "query_error": "",
        }
        if logger:
            logger.record(
                "sql_execution",
                node="execute_sql",
                sql_query=state["sql_query"],
                row_count=len(query_result),
            )
            logger.node_end("execute_sql", output)
        return output
    except Exception as error:
        output = {"query_result": [], "query_error": str(error)}
        if logger:
            logger.record(
                "sql_execution_error",
                node="execute_sql",
                sql_query=state["sql_query"],
                error=str(error),
            )
            logger.node_end("execute_sql", output)
        return output


def write_final_answer(
    state: AnalystState,
    llm: ChatOpenAI,
    logger: RunLogger | None = None,
) -> AnalystState:
    """Use OpenAI to explain the query result in plain English."""

    if logger:
        logger.node_start("write_final_answer", state)

    if not state["sql_is_safe"]:
        output = {
            "final_answer": (
                "I did not run the SQL query because it failed the read-only safety check: "
                f"{state['sql_validation_error']}"
            )
        }
        if logger:
            logger.node_end("write_final_answer", output)
        return output

    if state.get("query_error"):
        output = {
            "final_answer": (
                "I tried to run the generated SQL, but SQLite returned an error: "
                f"{state['query_error']}. The query needs to be revised."
            )
        }
        if logger:
            logger.node_end("write_final_answer", output)
        return output

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

    if logger:
        logger.llm_result("write_final_answer", response.content)

    output = {"final_answer": response.content}

    if logger:
        logger.node_end("write_final_answer", output)

    return output


def route_after_validation(state: AnalystState) -> str:
    """Decide whether to execute SQL or skip straight to the final answer."""

    if state["sql_is_safe"]:
        return "execute_sql"
    return "write_final_answer"


def build_graph(
    openai_api_key: str,
    openai_model: str,
    logger: RunLogger | None = None,
):
    """Build and compile the first version of the LangGraph workflow."""

    llm = ChatOpenAI(api_key=openai_api_key, model=openai_model)
    graph = StateGraph(AnalystState)

    graph.add_node("inspect_schema", lambda state: inspect_schema(state, logger))
    graph.add_node("classify_question", lambda state: classify_question(state, llm, logger))
    graph.add_node("generate_sql", lambda state: generate_sql(state, llm, logger))
    graph.add_node("validate_sql", lambda state: validate_sql(state, logger))
    graph.add_node("execute_sql", lambda state: execute_sql(state, logger))
    graph.add_node("write_final_answer", lambda state: write_final_answer(state, llm, logger))

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
