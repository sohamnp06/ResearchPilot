import { useEffect, useState } from "react";
import Navbar from "../components/Navbar/Navbar";
import "../styles/pages/reader.css";
import { useNavigate } from "react-router-dom";
import { getLibrary, getReaderProgress, uploadPaper } from "../lib/api";

function Reader() {
    const navigate = useNavigate();
    const [paper, setPaper] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
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

        load();
    }, []);

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

                        <button className="continue-button" onClick={() => navigate(`/reader/${paper.id}`)}>CONTINUE</button>
                    </article>
                ) : (
                    <p>No saved reading history yet.</p>
                )}
            </section>
        </main>
    );
}

export default Reader;