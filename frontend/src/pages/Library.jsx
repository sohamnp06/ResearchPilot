import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar/Navbar";
import { getLibrary, removeFromLibrary } from "../lib/api";

function Library() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hoveredPaperId, setHoveredPaperId] = useState(null);
  const navigate = useNavigate();

  async function loadLibrary() {
    try {
      const data = await getLibrary();
      setPapers(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLibrary();
  }, []);

  async function handleRemove(paperId) {
    const paper = papers.find((item) => item.id === paperId);
    const confirmed = window.confirm(`Remove "${paper?.title || "this paper"}" from your library?`);
    if (!confirmed) return;

    try {
      await removeFromLibrary(paperId);
      await loadLibrary();
    } catch (error) {
      console.error(error);
      alert("Could not remove paper from library");
    }
  }

  return (
    <main style={{ width: "min(1100px, 88vw)", margin: "0 auto", padding: "36px 0 80px" }}>
      <Navbar />

      <div style={{ marginTop: "52px" }}>
        <h1
          style={{
            margin: "0 0 24px",
            fontFamily: '"Instrument Serif", serif',
            fontSize: "72px",
            fontWeight: 400,
            lineHeight: 1,
            letterSpacing: "-0.04em",
            color: "#000",
          }}
        >
          LIBRARY
        </h1>

        {loading ? (
          <p style={{ fontFamily: '"Lexend Exa", sans-serif', fontSize: "15px", letterSpacing: ".08em" }}>Loading...</p>
        ) : papers.length === 0 ? (
          <div
            style={{
              border: "2px solid #000",
              background: "#FFF6EA",
              padding: "1.25rem 1.5rem",
              boxShadow: "6px 6px 0 #000",
              maxWidth: "420px",
            }}
          >
            <p style={{ margin: 0, fontFamily: '"Lexend Exa", sans-serif', fontSize: "15px", letterSpacing: ".08em" }}>
              No papers in library.
            </p>
          </div>
        ) : (
          <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: "16px" }}>
            {papers.map((paper) => {
              const authors = Array.isArray(paper.authors) ? paper.authors : [];
              const abstract = paper.abstract ? String(paper.abstract).trim() : "";
              const previewText = abstract.length > 180 ? `${abstract.slice(0, 177)}...` : abstract;

              return (
                <li
                  key={paper.id}
                  onMouseEnter={() => setHoveredPaperId(paper.id)}
                  onMouseLeave={() => setHoveredPaperId(null)}
                  style={{
                    border: "2px solid #000",
                    background: "#FFF6EA",
                    boxShadow: "6px 6px 0 #000",
                    padding: "18px 20px",
                    position: "relative",
                  }}
                >
                  {hoveredPaperId === paper.id && (
                    <div
                      style={{
                        position: "absolute",
                        top: "calc(100% + 10px)",
                        left: "20px",
                        width: "min(360px, 72%)",
                        background: "#111111",
                        color: "#F5F0E6",
                        border: "2px solid #000",
                        boxShadow: "6px 6px 0 #000",
                        padding: "12px 14px",
                        zIndex: 2,
                        fontFamily: '"Lexend Exa", sans-serif',
                        fontSize: "11px",
                        lineHeight: 1.6,
                        letterSpacing: ".03em",
                      }}
                    >
                      <div style={{ marginBottom: "8px", color: "#F6C470" }}>
                        {authors.length ? authors.slice(0, 3).join(", ") : "Author unknown"}
                      </div>
                      <div style={{ color: "#F5F0E6" }}>{previewText || "No abstract available."}</div>
                    </div>
                  )}

                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "12px", flexWrap: "wrap" }}>
                    <div>
                      <div
                        style={{
                          fontFamily: '"Lexend Exa", sans-serif',
                          fontSize: "11px",
                          letterSpacing: ".12em",
                          color: "#E63939",
                          marginBottom: "8px",
                          textTransform: "uppercase",
                        }}
                      >
                        {paper.source || "paper"}
                      </div>
                      <strong
                        style={{
                          fontFamily: '"Instrument Serif", serif',
                          fontSize: "32px",
                          fontWeight: 400,
                          lineHeight: 1.1,
                          color: "#000",
                          display: "block",
                        }}
                      >
                        {paper.title}
                      </strong>
                    </div>

                    <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
                      <button
                        type="button"
                        onClick={() => navigate(`/reader/${paper.id}`)}
                        style={{
                          border: "2px solid #000",
                          background: "#000",
                          color: "#FFF6EA",
                          fontFamily: '"Lexend Exa", sans-serif',
                          fontSize: "11px",
                          letterSpacing: ".12em",
                          padding: "10px 14px",
                          cursor: "pointer",
                          boxShadow: "4px 4px 0 #000",
                        }}
                      >
                        OPEN IN READER
                      </button>

                      <button
                        type="button"
                        onClick={() => handleRemove(paper.id)}
                        style={{
                          border: "2px solid #000",
                          background: "#FFF6EA",
                          color: "#000",
                          fontFamily: '"Lexend Exa", sans-serif',
                          fontSize: "11px",
                          letterSpacing: ".12em",
                          padding: "10px 14px",
                          cursor: "pointer",
                          boxShadow: "4px 4px 0 #000",
                        }}
                      >
                        REMOVE
                      </button>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </main>
  );
}

export default Library;
