import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar/Navbar";
import { getLibrary, removeFromLibrary } from "../lib/api";

import "../styles/pages/library.css";

function Library() {
    const [papers, setPapers] = useState([]);
    const [loading, setLoading] = useState(true);
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

        const confirmed = window.confirm(
            `Remove "${paper?.title || "this paper"}" from your library?`
        );

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
        <main className="library-page">
            <Navbar />

            <section className="library-header">
                <div>
                    <p className="library-kicker">YOUR COLLECTION</p>
                    <h1>LIBRARY</h1>
                </div>

                <button
                    type="button"
                    className="archive-view-button"
                    onClick={() => navigate("/archive")}
                >
                    ENTER ARCHIVE
                </button>
            </section>

            {loading ? (
                <div className="library-state">
                    <p>LOADING ARCHIVE...</p>
                </div>
            ) : papers.length === 0 ? (
                <div className="library-empty">
                    <p className="library-empty-label">ARCHIVE EMPTY</p>
                    <p>No papers in library.</p>
                </div>
            ) : (
                <section className="library-collection">
                    <div className="library-collection-header">
                        <span>{papers.length} PAPERS</span>
                        <span>YOUR ARCHIVE</span>
                    </div>

                    <ul className="library-grid">
                        {papers.map((paper, index) => {
                            const authors = Array.isArray(paper.authors)
                                ? paper.authors
                                : [];

                            const abstract = paper.abstract
                                ? String(paper.abstract).trim()
                                : "";

                            const previewText =
                                abstract.length > 180
                                    ? `${abstract.slice(0, 177)}...`
                                    : abstract;

                            return (
                                <li
                                    key={paper.id}
                                    className={`library-card library-card-${index % 4}`}
                                >
                                    <article className="library-paper">
                                        <div className="library-paper-top">
                                            <span className="library-paper-status">
                                                {paper.source || "PAPER"}
                                            </span>
                                        </div>

                                        <div className="library-paper-body">
                                            <h2>{paper.title}</h2>

                                            <div className="library-paper-meta">
                                                <span>
                                                    {paper.year || "YEAR N/A"}
                                                </span>

                                                <span>·</span>

                                                <span>
                                                    {authors.length
                                                        ? authors[0]
                                                        : "AUTHOR UNKNOWN"}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="library-paper-bottom">
                                            <span>
                                                {previewText
                                                    ? "ABSTRACT AVAILABLE"
                                                    : "NO ABSTRACT"}
                                            </span>

                                            <span>
                                                {paper.filename
                                                    ? "PDF"
                                                    : "DOCUMENT"}
                                            </span>
                                        </div>
                                    </article>

                                    <div className="library-card-actions">
                                        <button
                                            type="button"
                                            onClick={() =>
                                                navigate(
                                                    `/reader/${paper.id}`
                                                )
                                            }
                                        >
                                            OPEN IN READER
                                        </button>

                                        <button
                                            type="button"
                                            onClick={() =>
                                                handleRemove(paper.id)
                                            }
                                        >
                                            REMOVE
                                        </button>
                                    </div>
                                </li>
                            );
                        })}
                    </ul>
                </section>
            )}
        </main>
    );
}

export default Library;