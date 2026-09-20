"""Run a question, or the web placeholder."""

import sqlparse
import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from analyst.graph import graph

app = typer.Typer(
    no_args_is_help=True, 
    help="Ask a question about a US stock, or use 'web' to launch the web app.", 
    add_completion=False)


@app.command()
def web() -> None:
    """Run the web application (not implemented yet)."""
    typer.echo("Web app coming later.")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Financial question, enclosed in quotes."),
    query: bool = typer.Option(False, "--query", help="Print the formatted SQL after the results."),
) -> None:
    """Ask a question about a US stock."""
    state = graph.invoke({"question": question, "allowed_result_types": ["table"],
                          "ticker": "", "message": "", "query_attempts": 0, "error": ""})
    if not state["ticker"]:
        typer.echo(state["message"])
        return

    if state.get("final_message"):
        typer.echo()
        typer.echo(state["final_message"])
    if state.get("result_type") == "table" and state.get("columns"):
        table = Table(title=state["ticker"])
        for column in state["columns"]:
            table.add_column(column)
        for row in state["result"]:
            table.add_row(*(str(row[column]) if row[column] is not None else "—"
                            for column in state["columns"] ))
        typer.echo()
        Console().print(table)

    else:
        if state.get("result_type") != "table":
            typer.echo(f"Result type: {state.get('result_type')} invalid for CLI output.")
        elif not state.get("columns"):
            typer.echo("No columns returned for the query.")
    if query and state.get("query"):
        typer.echo()
        formatted_sql = sqlparse.format(state["query"], reindent=True, keyword_case="upper")
        Console().print(Syntax(formatted_sql, "sql", word_wrap=True))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
