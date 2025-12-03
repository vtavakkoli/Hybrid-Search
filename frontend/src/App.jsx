import React, { useState } from "react";
import axios from "axios";

// EXTERNAL PORT 4800
const API_URL = "http://localhost:4800";

// --- STYLES ---
const colors = {
  bg: "#f4f6f8",
  white: "#ffffff",
  primary: "#2196f3",
  qdrant: "#e91e63", // Pink
  elastic: "#00bfb3", // Teal
  text: "#333",
  subText: "#666",
  border: "#e0e0e0"
};

const styles = {
  container: {
    maxWidth: "1200px",
    margin: "0 auto",
    padding: "40px 20px",
    fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    color: colors.text,
    background: colors.bg,
    minHeight: "100vh"
  },
  header: { textAlign: "center", marginBottom: "40px" },
  title: { fontSize: "2.5rem", fontWeight: "700", marginBottom: "10px", color: "#2c3e50" },
  subtitle: { fontSize: "1.1rem", color: colors.subText },
  tabContainer: { display: "flex", justifyContent: "center", marginBottom: "30px", gap: "20px" },
  tab: (isActive) => ({
    padding: "12px 30px",
    fontSize: "1rem",
    fontWeight: "600",
    borderRadius: "30px",
    border: "none",
    cursor: "pointer",
    transition: "all 0.2s ease",
    background: isActive ? colors.primary : colors.white,
    color: isActive ? colors.white : colors.text,
    boxShadow: isActive ? "0 4px 12px rgba(33, 150, 243, 0.3)" : "0 2px 5px rgba(0,0,0,0.05)"
  }),
  card: {
    background: colors.white,
    padding: "30px",
    borderRadius: "16px",
    boxShadow: "0 4px 20px rgba(0,0,0,0.05)",
    marginBottom: "20px"
  },
  dropZone: {
    border: "2px dashed #cbd5e0",
    borderRadius: "12px",
    padding: "40px",
    textAlign: "center",
    background: "#f8fafc",
    cursor: "pointer",
    transition: "border 0.2s"
  },
  statGrid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px", marginTop: "30px" },
  statCard: { background: "#f8f9fa", padding: "20px", borderRadius: "12px", textAlign: "center", border: "1px solid colors.border" },
  splitView: { display: "flex", gap: "30px", marginTop: "20px" },
  column: {
    flex: 1,
    background: "#fff",
    borderRadius: "12px",
    padding: "20px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
    border: "1px solid #f0f0f0"
  },
  badge: (bg) => ({
    display: "inline-block",
    padding: "6px 12px",
    borderRadius: "20px",
    background: bg,
    color: "white",
    fontSize: "0.85rem",
    fontWeight: "bold",
    marginBottom: "15px",
    textTransform: "uppercase",
    letterSpacing: "0.5px"
  }),
  resultItem: {
    padding: "15px",
    marginBottom: "15px",
    borderRadius: "8px",
    background: "#fdfdfd",
    borderLeft: "4px solid #ddd",
    border: "1px solid #eee",
    borderLeftWidth: "4px",
    transition: "transform 0.1s"
  },
  input: {
    width: "100%",
    padding: "16px",
    fontSize: "1.1rem",
    borderRadius: "12px",
    border: "2px solid #e0e0e0",
    outline: "none",
    transition: "border-color 0.2s",
    boxSizing: "border-box"
  },
  button: {
    marginTop: "20px",
    padding: "14px 28px",
    fontSize: "1rem",
    background: colors.primary,
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontWeight: "600",
    width: "100%"
  },
  fileIcon: { marginRight: "8px", fontSize: "1.2em" },
  sourceText: { fontSize: "0.9rem", fontWeight: "700", color: "#555", marginBottom: "6px", display: "flex", alignItems: "center" }
};

// --- COMPONENT: Result Item ---
// Defined OUTSIDE App to prevent re-renders
const ResultCard = ({ r, color }) => (
  <div style={{...styles.resultItem, borderLeftColor: color}}>
    <div style={styles.sourceText}>
      <span style={styles.fileIcon}>📄</span> 
      {r.source}
    </div>
    <p style={{margin: "0 0 10px 0", lineHeight: "1.5", fontSize: "0.95rem", color: "#333"}}>
      {r.text}
    </p>
    <div style={{display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "#888"}}>
      <span>Relevance Score: <strong>{r.score.toFixed(4)}</strong></span>
    </div>
  </div>
);

// --- COMPONENT: Ingest Tab ---
const IngestView = ({ files, setFiles, handleIngest, loadingIngest, ingestStats }) => (
  <div style={styles.card}>
    <h2 style={{marginTop:0}}>📂 Upload Documents</h2>
    <p style={{color: "#666", marginBottom: "20px"}}>
      Upload PDFs, Text files, or CSVs. We will split them into chunks and vectorise them into both systems.
    </p>
    
    <div style={styles.dropZone}>
      <input 
        id="file-upload"
        name="file-upload"
        type="file" 
        multiple 
        onChange={(e) => setFiles(e.target.files)} 
        style={{marginBottom: "10px"}}
      />
      <label htmlFor="file-upload" style={{display:"block", marginTop: "10px", color: "#666"}}>
        Selected: {files ? files.length : 0} files
      </label>
    </div>

    <button style={styles.button} onClick={handleIngest} disabled={loadingIngest}>
      {loadingIngest ? "Processing & Vectorizing..." : "Start Ingestion Benchmark"}
    </button>

    {ingestStats && (
      <div style={{marginTop: "30px", animation: "fadeIn 0.5s"}}>
        <h3 style={{textAlign: "center", color: "green"}}>✅ Ingestion Complete</h3>
        
        <div style={styles.statGrid}>
          <div style={styles.statCard}>
            <div style={{fontSize: "2rem", fontWeight: "bold", color: "#333"}}>
              {ingestStats.chunks}
            </div>
            <div style={{color: "#666"}}>Total Chunks Created</div>
          </div>
          
          <div style={{...styles.statCard, borderTop: `4px solid ${colors.qdrant}`}}>
            <div style={{fontSize: "1.5rem", fontWeight: "bold", color: colors.qdrant}}>
              {ingestStats.qdrant_time_ms.toFixed(2)} ms
            </div>
            <div style={{color: "#666"}}>Qdrant Write Time</div>
          </div>

          <div style={{...styles.statCard, borderTop: `4px solid ${colors.elastic}`}}>
            <div style={{fontSize: "1.5rem", fontWeight: "bold", color: colors.elastic}}>
              {ingestStats.elastic_time_ms.toFixed(2)} ms
            </div>
            <div style={{color: "#666"}}>Elastic Write Time</div>
          </div>
        </div>
      </div>
    )}
  </div>
);

// --- COMPONENT: Search Tab ---
const SearchView = ({ query, setQuery, handleSearch, loadingSearch, searchStats }) => (
  <div>
    <div style={styles.card}>
      <form onSubmit={handleSearch}>
        {/* Added ID and Name to fix accessibility warning */}
        <input 
          id="search-input"
          name="search-query"
          autoComplete="off"
          style={styles.input} 
          value={query} 
          onChange={e => setQuery(e.target.value)} 
          placeholder="🔎 Ask a question or search for keywords..." 
        />
        <button style={styles.button} disabled={loadingSearch} type="submit">
          {loadingSearch ? "Running Hybrid Search..." : "Compare Performance"}
        </button>
      </form>
    </div>

    {searchStats && (
      <div style={styles.splitView}>
        {/* Qdrant Column */}
        <div style={styles.column}>
          <div style={{textAlign: "center", borderBottom: "1px solid #eee", paddingBottom: "15px", marginBottom: "15px"}}>
            <span style={styles.badge(colors.qdrant)}>Qdrant</span>
            <div style={{fontSize: "1.2rem", fontWeight: "bold"}}>
              {searchStats.qdrant_time_ms.toFixed(2)} ms
            </div>
          </div>
          {searchStats.qdrant_results.length === 0 && <p>No results found.</p>}
          {searchStats.qdrant_results.map((r, i) => (
            <ResultCard key={i} r={r} color={colors.qdrant} />
          ))}
        </div>

        {/* Elastic Column */}
        <div style={styles.column}>
          <div style={{textAlign: "center", borderBottom: "1px solid #eee", paddingBottom: "15px", marginBottom: "15px"}}>
            <span style={styles.badge(colors.elastic)}>Elasticsearch</span>
            <div style={{fontSize: "1.2rem", fontWeight: "bold"}}>
              {searchStats.elastic_time_ms.toFixed(2)} ms
            </div>
          </div>
          {searchStats.elastic_results.length === 0 && <p>No results found.</p>}
          {searchStats.elastic_results.map((r, i) => (
            <ResultCard key={i} r={r} color={colors.elastic} />
          ))}
        </div>
      </div>
    )}
  </div>
);

function App() {
  const [activeTab, setActiveTab] = useState("search"); 
  
  // Ingest State
  const [files, setFiles] = useState(null);
  const [ingestStats, setIngestStats] = useState(null);
  const [loadingIngest, setLoadingIngest] = useState(false);

  // Search State
  const [query, setQuery] = useState("");
  const [searchStats, setSearchStats] = useState(null);
  const [loadingSearch, setLoadingSearch] = useState(false);

  const handleIngest = async () => {
    if (!files) return;
    setLoadingIngest(true);
    setIngestStats(null);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) formData.append("files", files[i]);

    try {
      const res = await axios.post(`${API_URL}/ingest`, formData);
      setIngestStats(res.data);
    } catch (err) { alert("Error: " + err.message); }
    setLoadingIngest(false);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;
    setLoadingSearch(true);
    setSearchStats(null);
    try {
      const res = await axios.post(`${API_URL}/search`, { query, limit: 5 });
      setSearchStats(res.data);
    } catch (err) { alert("Error: " + err.message); }
    setLoadingSearch(false);
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>⚔️ Vector DB Benchmark</h1>
        <p style={styles.subtitle}>Hybrid Search Comparison: Qdrant vs Elasticsearch</p>
      </header>

      <div style={styles.tabContainer}>
        <button 
          style={styles.tab(activeTab === "ingest")} 
          onClick={() => setActiveTab("ingest")}
        >
          📂 Data Ingestion
        </button>
        <button 
          style={styles.tab(activeTab === "search")} 
          onClick={() => setActiveTab("search")}
        >
          🔍 Hybrid Search
        </button>
      </div>

      <div style={{animation: "fadeIn 0.3s"}}>
        {activeTab === "ingest" ? (
          <IngestView 
            files={files} 
            setFiles={setFiles} 
            handleIngest={handleIngest} 
            loadingIngest={loadingIngest} 
            ingestStats={ingestStats} 
          />
        ) : (
          <SearchView 
            query={query} 
            setQuery={setQuery} 
            handleSearch={handleSearch} 
            loadingSearch={loadingSearch} 
            searchStats={searchStats} 
          />
        )}
      </div>
      
      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}

export default App;
