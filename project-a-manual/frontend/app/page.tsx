"use client";

import { useState, useEffect, useCallback } from "react";

const API = "http://localhost:8000";
const API_KEY = "dev-api-key";

type Note = {
  id: number;
  title: string;
  body: string;
  tags: string[];
  created_at: string;
  updated_at: string;
};

const TAG_COLORS = ["color-orange", "color-blue", "color-pink", "color-green"];

function tagColor(tag: string) {
  let hash = 0;
  for (let i = 0; i < tag.length; i++) hash = tag.charCodeAt(i) + ((hash << 5) - hash);
  return TAG_COLORS[Math.abs(hash) % TAG_COLORS.length];
}

export default function Home() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [search, setSearch] = useState("");
  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<"create" | "edit" | null>(null);
  const [editing, setEditing] = useState<Note | null>(null);
  const [formTitle, setFormTitle] = useState("");
  const [formBody, setFormBody] = useState("");
  const [formTags, setFormTags] = useState("");

  const headers = { "Content-Type": "application/json", "X-API-Key": API_KEY };

  const fetchNotes = useCallback(async () => {
    setError(null);
    try {
      let url = `${API}/api/notes`;
      if (activeTag || search) {
        const params = new URLSearchParams();
        if (activeTag) params.set("tag", activeTag);
        if (search) params.set("q", search);
        url = `${API}/api/notes/search?${params}`;
      }
      const res = await fetch(url, { headers: { "X-API-Key": API_KEY } });
      if (!res.ok) throw new Error(`Failed to load notes (${res.status})`);
      setNotes(await res.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, [activeTag, search]);

  useEffect(() => { fetchNotes(); }, [fetchNotes]);

  const allTags = Array.from(new Set(notes.flatMap((n) => n.tags)));

  function openCreate() {
    setFormTitle("");
    setFormBody("");
    setFormTags("");
    setEditing(null);
    setModal("create");
  }

  function openEdit(note: Note) {
    setFormTitle(note.title);
    setFormBody(note.body);
    setFormTags(note.tags.join(", "));
    setEditing(note);
    setModal("edit");
  }

  async function handleSave() {
    setError(null);
    const tags = formTags.split(",").map((t) => t.trim()).filter(Boolean);
    const body = { title: formTitle, body: formBody, tags };

    try {
      let res;
      if (modal === "edit" && editing) {
        res = await fetch(`${API}/api/notes/${editing.id}`, {
          method: "PUT", headers, body: JSON.stringify(body),
        });
      } else {
        res = await fetch(`${API}/api/notes`, {
          method: "POST", headers, body: JSON.stringify(body),
        });
      }
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || `Error ${res.status}`);
      }
      setModal(null);
      fetchNotes();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save failed");
    }
  }

  async function handleDelete() {
    if (!editing) return;
    try {
      const res = await fetch(`${API}/api/notes/${editing.id}`, {
        method: "DELETE", headers: { "X-API-Key": API_KEY },
      });
      if (!res.ok) throw new Error(`Delete failed (${res.status})`);
      setModal(null);
      fetchNotes();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  return (
    <div className="v-container">
      <nav className="v-menu">
        <a className="v-menu_logo"></a>
        <a className="v-menu_link active">
          <svg width="16" height="16" viewBox="0 0 34 34" fill="none">
            <path d="M2 4.6c0-1.9 1.7-3.3 3.5-2.9l11 2c.3.1.7.1 1 0l11-2c1.8-.3 3.5 1.1 3.5 3v21.5c0 1.5-1.1 2.8-2.6 3l-12 1.8c-.3 0-.6 0-.9 0l-12-1.8C3.1 28.9 2 27.7 2 26.2V4.6z" stroke="white" strokeWidth="3"/>
            <line x1="17" y1="4" x2="17" y2="31" stroke="white" strokeWidth="2"/>
          </svg>
        </a>
        <a className="v-menu_link bottom">
          <svg width="18" height="4" viewBox="0 0 18 4" fill="none">
            <circle cx="2" cy="2" r="2" fill="white"/>
            <circle cx="9" cy="2" r="2" fill="white"/>
            <circle cx="16" cy="2" r="2" fill="white"/>
          </svg>
        </a>
      </nav>

      <h1 className="v-title">Note App</h1>

      <div className="v-header">
        <div className="v-search">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#999" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            type="text"
            placeholder="Search notes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {allTags.length > 0 && (
        <div className="v-tags">
          {allTags.map((tag) => (
            <span
              key={tag}
              className={`v-tag ${activeTag === tag ? "active" : ""}`}
              onClick={() => setActiveTag(activeTag === tag ? null : tag)}
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {error && <div className="v-error">{error}</div>}

      <div className="v-notes">
        {loading && <div className="v-loading">Loading...</div>}
        {!loading && notes.length === 0 && (
          <div className="v-empty">No notes yet. Create one!</div>
        )}
        {notes.map((note) => (
          <div key={note.id} className="v-section" onClick={() => openEdit(note)}>
            <div className="v-section_title">
              <span className={`v-section_line ${tagColor(note.tags[0] || "default")}`}></span>
              {note.title}
            </div>
            {note.body && <div className="v-section_body">{note.body}</div>}
            <div className="v-section_meta">
              <span className="v-section_time">
                {new Date(note.updated_at).toLocaleDateString()}
              </span>
              <div className="dots">
                {note.tags.map((tag) => (
                  <span key={tag} className={`dot ${tagColor(tag)}`}></span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <button className="v-btn" onClick={openCreate}>+ Add Note</button>

      {modal && (
        <div className="v-modal-overlay" onClick={() => setModal(null)}>
          <div className="v-modal" onClick={(e) => e.stopPropagation()}>
            <h2>{modal === "edit" ? "Edit Note" : "New Note"}</h2>
            <label>Title</label>
            <input value={formTitle} onChange={(e) => setFormTitle(e.target.value)} />
            <label>Body</label>
            <textarea value={formBody} onChange={(e) => setFormBody(e.target.value)} />
            <label>Tags (comma separated)</label>
            <input value={formTags} onChange={(e) => setFormTags(e.target.value)} placeholder="work, ideas, urgent" />
            <div className="v-modal-actions">
              {modal === "edit" && (
                <button className="btn-delete" onClick={handleDelete}>Delete</button>
              )}
              <button className="btn-cancel" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn-save" onClick={handleSave}>Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
