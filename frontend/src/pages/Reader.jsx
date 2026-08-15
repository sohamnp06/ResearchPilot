import { useEffect, useState } from "react";
import Navbar from "../components/Navbar/Navbar";
import "../styles/pages/reader.css";
import { useNavigate } from "react-router-dom";
import { getLibrary, getReaderProgress, removeFromReader, uploadPaper } from "../lib/api";

function Reader() {
    const navigate = useNavigate();
    const [paper, setPaper] = useState(null);
    const [loading, setLoading] = useState(true);

    async function load() {
        try {
            const progress = await getReaderProgress();
            if (progress.paper_id) {
                const library = await getLibrary();
                const match = library.find((item) => item.id === progress.paper_id);
                setPaper(match || { id: progress.paper_id, title: "Saved paper", year: "—", source: "local" });
            } else {
                const library = await getLibrary();
                setPaper(library[0] || null);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        load();
    }, []);

    async function handleRemove(paperId) {
        const confirmed = window.confirm(`Remove "${paper?.title || "this paper"}" from your reading history?`);
        if (!confirmed) return;

        try {
            await removeFromReader(paperId);
            await load();
        } catch (error) {
            console.error(error);
            alert("Could not remove paper from reader");
        }
    }

    async function handleUpload(event) {
        const file = event.target.files?.[0];
        if (!file) return;

        try {
            const result = await uploadPaper(file);
            navigate(`/reader/${result.id}`);
        } catch (error) {
            console.error(error);
            alert("Upload failed");
        }
    }

    return (
        <main className="reader-page">
            <Navbar />

            <div className="reader-toolbar">
                <label className="reader-upload" style={{ cursor: "pointer" }}>
                    UPLOAD
                    <input type="file" accept="application/pdf" hidden onChange={handleUpload} />
                </label>
            </div>

            <section className="reading-history">
                {loading ? (
                    <p>Loading your reading history...</p>
                ) : paper ? (
                    <article className="reading-card">
                        <div className="reading-info">
                            <span className="reading-id">{paper.id}</span>
                            <h1>{paper.title}</h1>
                            <div className="reading-meta">
                                <span>{paper.year}</span>
                                <span>|</span>
                                <span>{paper.source}</span>
                            </div>
                        </div>

                        <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
                            <button className="continue-button" onClick={() => navigate(`/reader/${paper.id}`)}>CONTINUE</button>
                            <button
                                type="button"
                                className="continue-button"
                                onClick={() => handleRemove(paper.id)}
                                style={{ background: "#FFF6EA", color: "#000", border: "2px solid #000", boxShadow: "4px 4px 0 #000" }}
                            >
                                REMOVE
                            </button>
                        </div>
                    </article>
                ) : (
                    <p>No saved reading history yet.</p>
                )}
            </section>
        </main>
    );
}

export default Reader;