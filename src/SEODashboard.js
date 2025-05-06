import React, { useState } from "react";

export default function SEODashboard() {
  const [url, setUrl] = useState("");
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const runAudit = async () => {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await fetch("/audit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url, target_keyword: keyword }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }

      const data = await res.json();

      if (!data.seo_score || !data.meta_tags || !data.competitor_comparison) {
        throw new Error('Unexpected response format from the server.');
      }

      setResult(data);
    } catch (error) {
      console.error("Audit failed:", error);
      setError(error.message);
      alert(`Failed to run audit: ${error.message}. Check console for details.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "auto" }}>
      <h1>🔍 SEO Audit Tool</h1>
      <input
        type="text"
        placeholder="Website URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        style={{ display: "block", marginBottom: "1rem", width: "100%" }}
      />
      <input
        type="text"
        placeholder="Target Keyword"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        style={{ display: "block", marginBottom: "1rem", width: "100%" }}
      />
      <button onClick={runAudit} disabled={loading}>
        {loading ? "Running Audit..." : "Run Audit"}
      </button>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {result && (
        <div style={{ marginTop: "2rem" }}>
          <h2>SEO Score: {result.seo_score}</h2>
          <pre>{JSON.stringify(result.meta_tags, null, 2)}</pre>
          <h3>Top Competitors:</h3>
          <ul>
            {result.competitor_comparison.map((comp, i) => (
              <li key={i}>{comp.url}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
