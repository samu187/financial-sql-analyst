"""Command line entry point for the LangGraph Financial Analyst app."""

from __future__ import annotations

from financial_analyst_langgraph.config import load_settings
from financial_analyst_langgraph.database import seed_sample_company
from financial_analyst_langgraph.graph import build_graph


def main() -> None:
    """Run the first CLI version of the app."""

    settings = load_settings()

    print("\nLangGraph Financial Analyst")
    print("===========================")
    print("This first version prepares the database we will use for the LangGraph workflow.\n")

    while True:
        print("Choose a data source:")
        print("1. Use sample company")
        print("2. Select ticker with Alpha Vantage")

        choice = input("\nEnter 1 or 2: ").strip()

        if choice == "1":
            company_id = seed_sample_company(settings.database_path)
            graph = build_graph()
            result = graph.invoke(
                {
                    "database_path": str(settings.database_path),
                    "user_question": "What financial data is available?",
                }
            )

            print("\nSample company loaded.")
            print(f"Company ID: {company_id}")
            print(f"Database path: {settings.database_path}")
            print("\nDatabase schema:")
            print(result["schema_summary"])
            print("\nLangGraph ran one node: inspect_schema.")
            print("Next step: we will add a node that accepts a financial question.")
            return

        if choice == "2":
            print("\nTicker import is not available yet.")
            print("For now, please choose the sample company so we can build the graph together.\n")
            continue

        print("\nPlease enter 1 or 2.\n")


if __name__ == "__main__":
    main()
