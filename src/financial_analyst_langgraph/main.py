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
            if not settings.openai_api_key:
                print("\nOpenAI API key not found.")
                print("Create a .env file from .env.example and add OPENAI_API_KEY.")
                return

            user_question = input(
                "\nAsk a financial question about Sample Manufacturing Co.\n> "
            ).strip()
            if not user_question:
                user_question = "Show revenue growth over the last five years."

            graph = build_graph(
                openai_api_key=settings.openai_api_key,
                openai_model=settings.openai_model,
            )
            result = graph.invoke(
                {
                    "database_path": str(settings.database_path),
                    "user_question": user_question,
                }
            )

            print("\nSample company loaded.")
            print(f"Company ID: {company_id}")
            print(f"Database path: {settings.database_path}")
            print("\nDatabase schema:")
            print(result["schema_summary"])
            print("\nQuestion classification:")
            print(f"Intent: {result['question_intent']}")
            print(f"Response format: {result['response_format']}")
            print(f"Relevant tables: {', '.join(result['relevant_tables'])}")
            print(f"Reasoning: {result['classification_reasoning']}")
            print("\nGenerated SQL:")
            print(result["sql_query"])
            print(f"SQL safety: {'safe' if result['sql_is_safe'] else 'unsafe'}")
            if result["sql_validation_error"]:
                print(f"SQL validation error: {result['sql_validation_error']}")
            print("\nQuery result:")
            print(result["query_result"])
            print("\nFinal answer:")
            print(result["final_answer"])
            print(
                "\nLangGraph ran: inspect_schema -> classify_question -> "
                "generate_sql -> validate_sql -> execute_sql -> write_final_answer."
            )
            return

        if choice == "2":
            print("\nTicker import is not available yet.")
            print("For now, please choose the sample company so we can build the graph together.\n")
            continue

        print("\nPlease enter 1 or 2.\n")


if __name__ == "__main__":
    main()
