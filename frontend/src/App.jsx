import React, { useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:4800";
const palette = {
  bg: "#f5f7fb", ink: "#172033", muted: "#667085", blue: "#2563eb",
  qdrant: "#e91e63", elastic: "#00a99d", queryweave: "#6d4aff", border: "#e5e7eb",
};

const shell = { maxWidth: 1500, margin: "0 auto", padding: "36px 22px 60px", fontFamily: "Inter, Segoe UI, sans-serif", color: palette.ink };
const card = { background: "white", border: `1px solid ${palette.border}`, borderRadius: 16, padding: 24, boxShadow: "0 12px 35px rgba(16,24,40,.06)" };
const button = { border: 0, borderRadius: 10, background: palette.blue, color: "white", padding: "13px 20px", fontWeight: 700, cursor: "pointer" };

function ResultCard({ item, color }) {
  const exp = item.details?.explanation;
  return <div style={{ border: `1px solid ${palette.border}`, borderLeft: `4px solid ${color}`, borderRadius: 10, padding: 14, marginBottom: 12 }}>
    <div style={{ fontSize: 12, color: palette.muted, marginBottom: 6 }}>{item.source || "unknown source"}</div>
    <div style={{ lineHeight: 1.45 }}>{item.text}</div>
    <div style={{ marginTop: 9, fontSize: 12, color: palette.muted }}>score <b>{Number(item.score).toFixed(4)}</b></div>
    {exp && <div style={{ marginTop: 8, fontSize: 11, color: palette.muted }}>
      route <b>{exp.route}</b> · L/S/D {exp.weights.lexical.toFixed(2)}/{exp.weights.sparse.toFixed(2)}/{exp.weights.dense.toFixed(2)}
      {exp.reranked ? ` · reranked (${exp.reranker})` : ""}
    </div>}
  </div>;
}

function EngineColumn({ title, color, time, results, meta }) {
  return <section style={card}>
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
      <div><div style={{ fontWeight: 800, color }}>{title}</div>{meta && <div style={{ fontSize: 12, color: palette.muted }}>{meta}</div>}</div>
      <div style={{ fontSize: 20, fontWeight: 800 }}>{Number(time || 0).toFixed(2)} <span style={{ fontSize: 11, color: palette.muted }}>ms</span></div>
    </div>
    {results?.length ? results.map((r, i) => <ResultCard key={`${title}-${i}`} item={r} color={color} />) : <div style={{ color: palette.muted }}>No results</div>}
  </section>;
}

export default function App() {
  const [tab, setTab] = useState("search");
  const [files, setFiles] = useState(null);
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("auto");
  const [ingest, setIngest] = useState(null);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  async function ingestFiles() {
    if (!files?.length) return;
    setBusy(true); setIngest(null);
    try {
      const data = new FormData();
      [...files].forEach(file => data.append("files", file));
      setIngest((await axios.post(`${API_URL}/ingest`, data)).data);
    } catch (error) { alert(error.message); }
    finally { setBusy(false); }
  }

  async function runSearch(event) {
    event.preventDefault();
    if (!query.trim()) return;
    setBusy(true); setResult(null);
    try { setResult((await axios.post(`${API_URL}/search`, { query, limit: 5, queryweave_mode: mode })).data); }
    catch (error) { alert(error.message); }
    finally { setBusy(false); }
  }

  return <main style={{ background: palette.bg, minHeight: "100vh" }}><div style={shell}>
    <header style={{ marginBottom: 26 }}>
      <div style={{ color: palette.queryweave, fontWeight: 800, letterSpacing: 1, fontSize: 13 }}>HYBRID SEARCH LAB</div>
      <h1 style={{ fontSize: 38, margin: "7px 0 8px" }}>One corpus. One embedding stack. Three search engines.</h1>
      <p style={{ color: palette.muted, maxWidth: 850, margin: 0 }}>Qdrant RRF vs Elasticsearch hybrid retrieval vs QueryWeave adaptive query fusion, using the same BGE dense and SPLADE sparse vectors.</p>
    </header>

    <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
      {["search", "ingest"].map(x => <button key={x} onClick={() => setTab(x)} style={{ ...button, background: tab === x ? palette.ink : "white", color: tab === x ? "white" : palette.ink, border: `1px solid ${palette.border}` }}>{x === "search" ? "Search benchmark" : "Data ingestion"}</button>)}
    </div>

    {tab === "ingest" ? <section style={card}>
      <h2>Index the same chunks in all engines</h2>
      <p style={{ color: palette.muted }}>Parsing and embedding happen once. Only backend write time is compared.</p>
      <input type="file" multiple onChange={e => setFiles(e.target.files)} />
      <button style={{ ...button, marginLeft: 14 }} disabled={busy} onClick={ingestFiles}>{busy ? "Processing…" : "Ingest & compare"}</button>
      {ingest && <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 12, marginTop: 24 }}>
        {[["chunks", ingest.chunks], ["embedding", `${ingest.embedding_time_ms.toFixed(1)} ms`], ["Qdrant", `${ingest.qdrant_time_ms.toFixed(1)} ms`], ["Elasticsearch", `${ingest.elastic_time_ms.toFixed(1)} ms`], ["QueryWeave", `${ingest.queryweave_time_ms.toFixed(1)} ms`]].map(([k,v]) => <div key={k} style={{ padding: 16, background: palette.bg, borderRadius: 10 }}><b>{v}</b><div style={{ color: palette.muted, fontSize: 12 }}>{k}</div></div>)}
      </div>}
    </section> : <>
      <form onSubmit={runSearch} style={{ ...card, marginBottom: 18, display: "grid", gridTemplateColumns: "1fr auto auto", gap: 10 }}>
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search exact identifiers or semantic questions…" style={{ padding: 14, border: `1px solid ${palette.border}`, borderRadius: 10, fontSize: 16 }} />
        <select value={mode} onChange={e => setMode(e.target.value)} style={{ padding: "0 14px", border: `1px solid ${palette.border}`, borderRadius: 10 }}>
          <option value="auto">QueryWeave: auto</option><option value="lexical">lexical</option><option value="hybrid">hybrid</option><option value="deep">deep</option>
        </select>
        <button style={button} disabled={busy}>{busy ? "Searching…" : "Compare"}</button>
      </form>
      {result && <>
        <div style={{ margin: "0 0 14px", color: palette.muted, fontSize: 13 }}>Shared query embedding: <b>{result.embedding_time_ms.toFixed(2)} ms</b> · QueryWeave route: <b>{result.queryweave_meta.route}</b></div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,minmax(0,1fr))", gap: 16 }}>
          <EngineColumn title="Qdrant" color={palette.qdrant} time={result.qdrant_time_ms} results={result.qdrant_results} meta="Dense + SPLADE · RRF" />
          <EngineColumn title="Elasticsearch" color={palette.elastic} time={result.elastic_time_ms} results={result.elastic_results} meta="BM25 + dense kNN" />
          <EngineColumn title="QueryWeave" color={palette.queryweave} time={result.queryweave_time_ms} results={result.queryweave_results} meta={`AQF · ${result.queryweave_meta.route}`} />
        </div>
      </>}
    </>}
  </div></main>;
}
