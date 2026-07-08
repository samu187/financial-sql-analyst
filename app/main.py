"""FastAPI entry point for the LangGraph Financial Analyst app."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import load_settings
from app.database import seed_sample_company
from app.graph import build_graph
from app.run_logger import RunLogger


STATIC_DIR = Path(__file__).resolve().parent / "static"


class AnalyzeRequest(BaseModel):
    """Request body for asking the financial analyst a question."""

    question: str = Field(min_length=1)
    data_source: Literal["sample", "ticker"] = "sample"


class AnalyzeResponse(BaseModel):
    """Response returned by the LangGraph financial analyst workflow."""

    answer: str
    generated_sql: str
    query_result: list[dict[str, Any]]
    query_error: str
    sql_is_safe: bool
    sql_validation_error: str
    question_intent: str
    relevant_tables: list[str]
    debug_log_path: str


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    api = FastAPI(
        title="LangGraph Financial Analyst",
        description="A FastAPI + React app powered by LangGraph and OpenAI.",
        version="0.1.0",
    )

    @api.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @api.post("/api/analyze", response_model=AnalyzeResponse)
    def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
        if request.data_source == "ticker":
            raise HTTPException(
                status_code=501,
                detail="Ticker import is not available yet. Please use the sample company.",
            )

        settings = load_settings()
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=400,
                detail="OPENAI_API_KEY is missing. Add it to your local .env file.",
            )

        seed_sample_company(settings.database_path)
        logger = RunLogger(log_path=Path.cwd() / "log.json")
        graph = build_graph(
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            logger=logger,
        )
        try:
            result = graph.invoke(
                {
                    "database_path": str(settings.database_path),
                    "user_question": request.question,
                }
            )
        except Exception as error:
            logger.record("graph_error", error=str(error))
            logger.write(final_state={"error": str(error)})
            raise HTTPException(status_code=500, detail=str(error)) from error
        else:
            logger.write(final_state=result)

        return AnalyzeResponse(
            answer=result["final_answer"],
            generated_sql=result.get("sql_query", ""),
            query_result=result.get("query_result", []),
            query_error=result.get("query_error", ""),
            sql_is_safe=result.get("sql_is_safe", False),
            sql_validation_error=result.get("sql_validation_error", ""),
            question_intent=result.get("question_intent", "unknown"),
            relevant_tables=result.get("relevant_tables", []),
            debug_log_path=str(logger.log_path),
        )

    if STATIC_DIR.exists():
        api.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

        @api.get("/{path:path}", include_in_schema=False)
        def serve_frontend(path: str) -> FileResponse:
            requested_path = STATIC_DIR / path
            if path and requested_path.is_file():
                return FileResponse(requested_path)
            return FileResponse(STATIC_DIR / "index.html")

    return api


app = create_app()


def start() -> None:
    """Run the app with `uv run start`."""

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    start()
