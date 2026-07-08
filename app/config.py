"""Application configuration."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the financial analyst app."""

    database_path: Path = PROJECT_ROOT / "data" / "sample_financials.sqlite"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4-mini"


def load_settings() -> Settings:
    """Load app settings.

    Values from `.env` stay local to your machine and are not committed to Git.
    """

    load_dotenv(PROJECT_ROOT / ".env")

    return Settings(
        database_path=Path(os.getenv("DATABASE_PATH", PROJECT_ROOT / "data" / "sample_financials.sqlite")),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
    )
