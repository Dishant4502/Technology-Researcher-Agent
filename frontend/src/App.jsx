import { useEffect, useState, startTransition } from "react";

import { KnowledgeList } from "./components/KnowledgeList";
import { RagChat } from "./components/RagChat";
import { ReportView } from "./components/ReportView";
import { ResearchForm } from "./components/ResearchForm";
import { fetchEntries, fetchEntry, runResearch } from "./lib/api";

const KNOWLEDGE_RETENTION_LIMIT = 8;
const initialForm = {
  query: "",
};

export default function App() {
  const [mode, setMode] = useState("research"); // "research" or "rag"
  const [form, setForm] = useState(initialForm);
  const [entries, setEntries] = useState([]);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchEntries()
      .then((data) => {
        startTransition(() => setEntries(data.slice(0, KNOWLEDGE_RETENTION_LIMIT)));
      })
      .catch((err) => setError(err.message));
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const query = form.query.trim();
    if (!query) {
      return;
    }
    setIsLoading(true);
    setError("");
    setForm(initialForm);

    try {
      const data = await runResearch({ query });
      startTransition(() => {
        setResult(data);
        setEntries((current) =>
          [data.entry, ...current.filter((item) => item.entry_id !== data.entry.entry_id)].slice(
            0,
            KNOWLEDGE_RETENTION_LIMIT,
          ),
        );
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  function handleNewResearch() {
    setResult(null);
    setForm(initialForm);
    setError("");
  }

  async function handleOpenEntry(entryId) {
    setError("");
    try {
      const data = await fetchEntry(entryId);
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="mode-toggle">
          <button
            className={`toggle-btn ${mode === "research" ? "active" : ""}`}
            onClick={() => setMode("research")}
          >
            Research Agent
          </button>
          <button
            className={`toggle-btn ${mode === "rag" ? "active" : ""}`}
            onClick={() => setMode("rag")}
          >
            Document Chat
          </button>
        </div>
        <button className="new-chat-button" type="button" onClick={handleNewResearch}>
          + New Research
        </button>
        <KnowledgeList entries={entries} onOpenEntry={handleOpenEntry} />
      </aside>

      <section className="main-pane">
        <header className="topbar">
          <h1>Technology Researcher</h1>
          <p>Autonomous market intelligence workspace</p>
        </header>

        {mode === "research" ? (
          <>
            <div className="conversation-area">
              {error ? <div className="error-banner">{error}</div> : null}
              <ReportView result={result} />
            </div>

            <ResearchForm form={form} onChange={handleChange} onSubmit={handleSubmit} isLoading={isLoading} />
          </>
        ) : (
          <RagChat />
        )}
      </section>
    </main>
  );
}
