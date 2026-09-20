"""Serve the frontend and run financial questions through the graph."""

import os
from pathlib import Path
from threading import Lock
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from analyst.graph import graph

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
_graph_lock = Lock()


class ChatMessage(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class QuestionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1)
    messages: list[ChatMessage] = Field(default_factory=list, description="Previous conversation turns, excluding the current question.")
    allowed_result_types: list[Literal["table", "linechart", "barchart"]] = Field(
        default_factory=lambda: ["table", "linechart", "barchart"], min_length=1
    )


@app.post("/ask")
def ask(request: QuestionRequest) -> dict:
    """Return the complete graph state for a financial question."""
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise HTTPException(
            status_code=503,
            detail=(
                "OpenAI API key is missing. Set OPENAI_API_KEY in the terminal "
                "that starts the web server, then restart the server."
            ),
        )
    # The downloader replaces a shared database; serialize runs in this server.
    with _graph_lock:
        return graph.invoke({
            "question": request.question,
            "messages": [message.model_dump() for message in request.messages],
            "allowed_result_types": request.allowed_result_types,
            "ticker": "",
            "message": "",
            "query_attempts": 0,
            "error": "",
        })


# Register API routes first so the frontend mount does not intercept them.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="frontend")
