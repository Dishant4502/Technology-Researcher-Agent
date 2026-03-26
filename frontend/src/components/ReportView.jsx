import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function ReportView({ result }) {
  if (!result) {
    return (
      <section className="conversation">
        <article className="message assistant empty-state">
          <h2>Start a new technology research thread</h2>
          <p>
            Enter a question below. The agent will search the web, synthesize findings, and save the final report
            to your knowledge repository.
          </p>
        </article>
      </section>
    );
  }

  return (
    <section className="conversation">
      <article className="message user">
        <p>{result.entry.query}</p>
      </article>

      <article className="message assistant">
        <h2>{result.entry.title}</h2>
        <div className="report-markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.raw_report}</ReactMarkdown>
        </div>
      </article>
    </section>
  );
}
