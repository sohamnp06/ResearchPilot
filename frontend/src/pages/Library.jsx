import { useEffect, useState } from "react";
import Navbar from "../components/Navbar/Navbar";
import { getLibrary } from "../lib/api";

function Library() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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

    loadLibrary();
  }, []);

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
            {papers.map((paper) => (
              <li
                key={paper.id}
                style={{
                  border: "2px solid #000",
                  background: "#FFF6EA",
                  boxShadow: "6px 6px 0 #000",
                  padding: "18px 20px",
                }}
              >
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
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}

export default Library;
