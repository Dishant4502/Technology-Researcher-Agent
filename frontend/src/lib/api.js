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
