"""Structured run logging for LangGraph executions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


def _json_safe(value: Any) -> Any:
    """Convert common Python objects into JSON-serializable values."""

    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]
    if hasattr(value, "model_dump"):
        return _json_safe(value.model_dump())
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, str | int | float | bool) or value is None:
        return value
    return str(value)


@dataclass
class RunLogger:
    """Collect and persist debug events for one analysis run."""

    log_path: Path
    run_id: str = field(default_factory=lambda: str(uuid4()))
    events: list[dict[str, Any]] = field(default_factory=list)

    def record(self, event_type: str, **payload: Any) -> None:
        self.events.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event_type": event_type,
                **_json_safe(payload),
            }
        )

    def node_start(self, node: str, state: dict[str, Any]) -> None:
        self.record(
            "node_start",
            node=node,
            available_state_keys=sorted(state.keys()),
        )

    def node_end(self, node: str, output: dict[str, Any]) -> None:
        self.record("node_end", node=node, output=output)

    def llm_result(self, node: str, result: Any) -> None:
        self.record("llm_result", node=node, result=result)

    def write(self, final_state: dict[str, Any] | None = None) -> None:
        document = {
            "run_id": self.run_id,
            "created_at": datetime.now(UTC).isoformat(),
            "final_state": _json_safe(final_state or {}),
            "events": self.events,
        }
        self.log_path.write_text(json.dumps(document, indent=2), encoding="utf-8")
