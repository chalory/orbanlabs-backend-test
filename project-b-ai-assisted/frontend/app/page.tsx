"use client";

import { useState, useEffect, useCallback } from "react";

const API = "http://localhost:8000";
const API_KEY = "dev-api-key";

type Link = {
  id: number;
  short_code: string;
  original_url: string;
  short_url: string;
  click_count: number;
  created_at: string;
  updated_at: string;
};

export default function Home() {
  const [links, setLinks] = useState<Link[]>([]);
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [copied, setCopied] = useState(false);

  const fetchLinks = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/links`, { headers: { "X-API-Key": API_KEY } });
      if (!res.ok) throw new Error(`Failed to load links (${res.status})`);
      setLinks(await res.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load links");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchLinks(); }, [fetchLinks]);

  async function handleShorten() {
    if (!url.trim()) return;
    setError(null);
    setResult(null);
    setSubmitting(true);
    try {
      const res = await fetch(`${API}/api/links`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
        body: JSON.stringify({ original_url: url }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || `Error ${res.status}`);
      }
      const data = await res.json();
      setResult(data.short_url);
      setUrl("");
      fetchLinks();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to shorten URL");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(code: string) {
    try {
      await fetch(`${API}/api/links/${code}`, {
        method: "DELETE",
        headers: { "X-API-Key": API_KEY },
      });
      fetchLinks();
    } catch {
      setError("Failed to delete link");
    }
  }

  function handleCopy() {
    if (!result) return;
    navigator.clipboard.writeText(result);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="container">
      <h1>URL Shortener</h1>

      <div className="shorten-form">
        <input
          type="text"
          placeholder="Paste a long URL here..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleShorten()}
        />
        <button onClick={handleShorten} disabled={submitting}>
          {submitting ? "..." : "Shorten"}
        </button>
      </div>

      {result && (
        <div className="result">
          <span>{result}</span>
          <button onClick={handleCopy}>{copied ? "Copied!" : "Copy"}</button>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {loading && <div className="loading">Loading...</div>}

      {!loading && links.length === 0 && (
        <div className="empty">No links yet. Shorten one above!</div>
      )}

      {!loading && links.length > 0 && (
        <table className="links-table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Original URL</th>
              <th>Clicks</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {links.map((link) => (
              <tr key={link.id}>
                <td className="code">{link.short_code}</td>
                <td className="url">{link.original_url}</td>
                <td className="clicks">{link.click_count}</td>
                <td>
                  <button className="delete-btn" onClick={() => handleDelete(link.short_code)}>
                    x
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
