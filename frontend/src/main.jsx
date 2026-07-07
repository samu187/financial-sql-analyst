import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Database, Loader2, Send, ShieldCheck, Sparkles } from "lucide-react";
import "./styles.css";

const EXAMPLE_QUESTIONS = [
  "Show revenue growth over the last five years.",
  "What's the coefficient of variation of revenues and the average annual increase?",
  "Compare net income and free cash flow from 2020 to 2024.",
  "What is the current ratio for each year?",
];

function formatCell(value) {
  if (typeof value === "number") {
    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: Math.abs(value) < 1 ? 4 : 0,
    }).format(value);
  }
  return String(value);
}

function ResultTable({ rows }) {
  const columns = useMemo(() => {
    if (!rows?.length) return [];
    return Object.keys(rows[0]);
  }, [rows]);

  if (!rows?.length) {
    return <p className="muted">No rows returned.</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column.replaceAll("_", " ")}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => (
                <td key={column}>{formatCell(row[column])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  const [question, setQuestion] = useState(EXAMPLE_QUESTIONS[0]);
  const [dataSource, setDataSource] = useState("sample");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function analyze(event) {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, data_source: dataSource }),
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "The analysis request failed.");
      }

      setResult(payload);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <div className="intro">
          <div>
            <p className="eyebrow">LangGraph + SQLite + OpenAI</p>
            <h1>Financial Analyst</h1>
          </div>
          <div className="status-pill">
            <ShieldCheck size={16} />
            read-only SQL
          </div>
        </div>

        <form className="question-panel" onSubmit={analyze}>
          <label htmlFor="data-source">Data source</label>
          <select
            id="data-source"
            value={dataSource}
            onChange={(event) => setDataSource(event.target.value)}
          >
            <option value="sample">Sample Manufacturing Co.</option>
            <option value="ticker">Ticker import (not available yet)</option>
          </select>

          <label htmlFor="question">Question</label>
          <textarea
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows={4}
          />

          <div className="examples">
            {EXAMPLE_QUESTIONS.map((example) => (
              <button
                key={example}
                type="button"
                className="example-button"
                onClick={() => setQuestion(example)}
              >
                {example}
              </button>
            ))}
          </div>

          <button className="submit-button" type="submit" disabled={isLoading}>
            {isLoading ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
            Analyze
          </button>
        </form>
      </section>

      <section className="results">
        {!result && !error && (
          <div className="empty-state">
            <Sparkles size={28} />
            <h2>Ask a finance question</h2>
            <p>
              The graph will inspect the schema, generate safe SQL, execute it, and
              summarize the findings.
            </p>
          </div>
        )}

        {error && (
          <div className="error-box">
            <h2>Request failed</h2>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="answer-stack">
            <div className="answer-card">
              <div className="card-title">
                <Sparkles size={18} />
                Answer
              </div>
              <p>{result.answer}</p>
            </div>

            <div className="meta-grid">
              <div>
                <span>Intent</span>
                <strong>{result.question_intent}</strong>
              </div>
              <div>
                <span>SQL safety</span>
                <strong>{result.sql_is_safe ? "safe" : "blocked"}</strong>
              </div>
              <div>
                <span>Tables</span>
                <strong>{result.relevant_tables.join(", ") || "none"}</strong>
              </div>
            </div>

            <div className="answer-card">
              <div className="card-title">
                <Database size={18} />
                Generated SQL
              </div>
              <pre>{result.generated_sql}</pre>
              {result.sql_validation_error && (
                <p className="error-text">{result.sql_validation_error}</p>
              )}
              {result.query_error && <p className="error-text">{result.query_error}</p>}
            </div>

            <div className="answer-card">
              <div className="card-title">
                <Database size={18} />
                Query Result
              </div>
              <ResultTable rows={result.query_result} />
            </div>
          </div>
        )}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
