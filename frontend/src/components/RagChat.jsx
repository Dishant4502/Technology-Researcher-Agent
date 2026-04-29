import { useState, useRef, useEffect } from "react";
import { uploadPdf, chatRag } from "../lib/api";

export function RagChat() {
  const [messages, setMessages] = useState([
    {
      role: "system",
      content: "Hello! Upload a technology document (PDF) above, and then ask me questions about it.",
    },
  ]);
  const [query, setQuery] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  async function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setIsUploading(true);
    setUploadStatus("Uploading and processing document...");
    try {
      const data = await uploadPdf(file);
      setUploadStatus(`Success! Processed ${data.chunks} chunks from ${file.name}.`);
    } catch (err) {
      setUploadStatus(`Error: ${err.message}`);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  async function handleChatSubmit(e) {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { role: "user", content: query.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setQuery("");
    setIsChatting(true);

    try {
      const data = await chatRag(userMessage.content);
      const systemMessage = {
        role: "system",
        content: data.answer,
        sources: data.sources,
      };
      setMessages((prev) => [...prev, systemMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "system", content: `Error: ${err.message}` },
      ]);
    } finally {
      setIsChatting(false);
    }
  }

  return (
    <div className="rag-container">
      <div className="rag-upload-area">
        <h3>Document Knowledge Base</h3>
        <p>Upload a PDF document to provide context for the assistant.</p>
        <div className="upload-controls">
          <input
            type="file"
            accept="application/pdf"
            ref={fileInputRef}
            onChange={handleFileChange}
            disabled={isUploading}
            className="file-input"
            id="pdf-upload"
          />
          <label htmlFor="pdf-upload" className="upload-button">
            {isUploading ? "Processing..." : "Select PDF"}
          </label>
        </div>
        {uploadStatus && <div className={`upload-status ${uploadStatus.startsWith('Error') ? 'error' : 'success'}`}>
          {uploadStatus}
        </div>}
      </div>

      <div className="rag-chat-area">
        <div className="messages-container">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-row ${msg.role}`}>
              <div className="message-bubble">
                <div className="message-content">{msg.content}</div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="message-sources">
                    <strong>Sources:</strong>
                    <ul>
                      {msg.sources.map((src, sIdx) => (
                        <li key={sIdx}>
                          Snippet from: {src.metadata?.source_filename || "Document"}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
          {isChatting && (
            <div className="message-row system">
              <div className="message-bubble loading">
                Thinking<span className="dot-one">.</span><span className="dot-two">.</span><span className="dot-three">.</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-form" onSubmit={handleChatSubmit}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about your document..."
            disabled={isChatting}
          />
          <button type="submit" disabled={isChatting || !query.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
