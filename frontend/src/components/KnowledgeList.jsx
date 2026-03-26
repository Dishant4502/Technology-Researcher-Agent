export function KnowledgeList({ entries, onOpenEntry }) {
  const visibleEntries = entries.slice(0, 8);

  return (
    <section className="repository-panel">
      <div className="sidebar-title">Knowledge Repository</div>
      <div className="repository-list">
        {visibleEntries.length === 0 ? (
          <p className="empty-copy">No saved reports yet.</p>
        ) : (
          visibleEntries.map((entry) => (
            <button
              key={entry.entry_id}
              type="button"
              className="repository-item"
              onClick={() => onOpenEntry(entry.entry_id)}
            >
              <h3>{entry.title}</h3>
              <p>{entry.summary}</p>
              <small>{new Date(entry.created_at).toLocaleString()}</small>
            </button>
          ))
        )}
      </div>
    </section>
  );
}
