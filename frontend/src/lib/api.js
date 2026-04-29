const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

export async function fetchEntries() {
  const response = await fetch(`${API_BASE}/research/entries`);
  if (!response.ok) {
    throw new Error("Failed to load knowledge repository.");
  }
  return response.json();
}

export async function fetchEntry(entryId) {
  const response = await fetch(`${API_BASE}/research/entries/${entryId}`);
  if (!response.ok) {
    throw new Error("Failed to load report.");
  }
  return response.json();
}

export async function runResearch(payload) {
  const response = await fetch(`${API_BASE}/research`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = "Research run failed.";
    try {
      const data = await response.json();
      if (typeof data?.detail === "string" && data.detail.trim()) {
        message = data.detail;
      }
    } catch {
      const text = await response.text();
      if (text.trim()) {
        message = text;
      }
    }
    throw new Error(message);
  }
  return response.json();
}

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/rag/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let message = "Document upload failed.";
    try {
      const data = await response.json();
      if (typeof data?.detail === "string" && data.detail.trim()) {
        message = data.detail;
      }
    } catch {
      // Fallback
    }
    throw new Error(message);
  }
  return response.json();
}

export async function chatRag(query) {
  const response = await fetch(`${API_BASE}/rag/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    let message = "Chat request failed.";
    try {
      const data = await response.json();
      if (typeof data?.detail === "string" && data.detail.trim()) {
        message = data.detail;
      }
    } catch {
      // Fallback
    }
    throw new Error(message);
  }
  return response.json();
}
