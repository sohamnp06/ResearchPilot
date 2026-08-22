import { useEffect, useState } from "react";
import Navbar from "../components/Navbar/Navbar";
import "../styles/pages/reader.css";
import { useNavigate } from "react-router-dom";
import {
    getPaperDetails,
    getReaderHistory,
    getReaderProgress,
    removeFromReader,
    uploadPaper
} from "../lib/api";

function Reader() {
    const navigate = useNavigate();

    const [papers, setPapers] = useState([]);
    const [loading, setLoading] = useState(true);

    async function load() {
        try {
            const history = await getReaderHistory();

            if (history.length > 0) {
                setPapers(history);
                return;
            }

            const progress = await getReaderProgress();

            if (progress?.paper_id) {
                const paper = await getPaperDetails(progress.paper_id);
                setPapers([paper]);
                return;
            }

            setPapers([]);
        } catch (error) {
            console.error(error);
            setPapers([]);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        load();
    }, []);

    async function handleRemove(paperId) {
        const target = papers.find((paper) => paper.id === paperId);

        const confirmed = window.confirm(
            `Remove "${target?.title || "this paper"}" from your reading history?`
        );

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
                <label className="reader-upload">
                    UPLOAD

                    <input
                        type="file"
                        accept="application/pdf"
                        hidden
                        onChange={handleUpload}
                    />
                </label>
            </div>

            <section className="reading-history">
                {loading ? (
                    <p className="reader-message">
                        Loading your reading history...
                    </p>
                ) : papers.length > 0 ? (
                    papers.map((paper) => (
                        <article
                            key={paper.id}
                            className="reading-card"
                        >
                            <div className="reading-info">
                                <h1>{paper.title}</h1>

                                <div className="reading-meta">
                                    <span>
                                        {paper.displayId || paper.display_id || "PAPER"}
                                    </span>

                                    <span>|</span>

                                    <span>
                                        {paper.year || "—"}
                                    </span>

                                    <span>|</span>

                                    <span>
                                        {paper.current_page
                                            ? `PAGE ${paper.current_page}`
                                            : "PAGE 1"}
                                    </span>
                                </div>
                            </div>

                            <div className="reading-actions">
                                <button
                                    className="continue-button"
                                    onClick={() =>
                                        navigate(`/reader/${paper.id}`)
                                    }
                                >
                                    CONTINUE →
                                </button>

                                <button
                                    type="button"
                                    className="remove-button"
                                    onClick={() =>
                                        handleRemove(paper.id)
                                    }
                                >
                                    REMOVE
                                </button>
                            </div>
                        </article>
                    ))
                ) : (
                    <p className="reader-message">
                        No saved reading history yet.
                    </p>
                )}
            </section>
        </main>
    );
}

export default Reader;