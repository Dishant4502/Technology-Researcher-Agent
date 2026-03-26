export function ResearchForm({ form, onChange, onSubmit, isLoading }) {
  return (
    <form className="composer" onSubmit={onSubmit}>
      <label className="composer-field">
        <textarea
          name="query"
          value={form.query}
          onChange={onChange}
          placeholder="Ask about product strategy, AI competition, funding trends, or enterprise technology shifts..."
          rows={3}
          required
        />
      </label>

      <button className="composer-button" type="submit" disabled={isLoading}>
        {isLoading ? "Researching..." : "Send"}
      </button>
    </form>
  );
}
