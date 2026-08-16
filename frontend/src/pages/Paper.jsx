import { useEffect, useState } from "react";
import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";
import { useNavigate, useParams } from "react-router-dom";
import { addToLibrary, getPaperDetails } from "../lib/api";

import "../styles/pages/paper.css";

function Paper() {
    const navigate = useNavigate();
    const { id } = useParams();
    const [paper, setPaper] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadPaper() {
            try {
                const data = await getPaperDetails(id);
                setPaper(data);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        }

        loadPaper();
    }, [id]);

    async function handleAddToLibrary() {
        try {
            await addToLibrary(paper.id);
            alert("Paper added to library");
        } catch (error) {
            console.error(error);
            alert("Could not add paper to library");
        }
    }

    if (loading) {
        return <main className="paper-page"><Navbar /><p>Loading paper...</p></main>;
    }

    if (!paper) {
        return <main className="paper-page"><Navbar /><p>Paper not found.</p></main>;
    }

    return (
        <main className="paper-page">
            <Navbar />

            <div className="paper-toolbar">
                <BackButton />

                <div className="paper-actions">
                    <button className="paper-action-button" onClick={handleAddToLibrary}>ADD TO LIBRARY</button>
                    <button className="paper-action-button" onClick={() => navigate(`/reader/${paper.id}`)}>READ PAPER</button>
                    <button className="paper-action-button" onClick={() => navigate(`/workspace/${paper.id}`)}>OPEN WORKSPACE</button>
                </div>
            </div>

            <section className="paper-layout">
                <div className="paper-info">
                    <div className="paper-number">{paper.id}</div>
                    <h1 className="paper-title">{paper.title}</h1>

                    <div className="paper-meta">
                        <span>{paper.year}</span>
                        <span>|</span>
                        <span>{paper.source}</span>
                    </div>

                    <section className="paper-section">
                        <h2>AUTHORS</h2>
                        <p className="paper-authors">
                            {(paper.authors || []).map((author, index) => (
                                <span key={`${author}-${index}`}>
                                    {author}
                                    {index < (paper.authors || []).length - 1 && " , "}
                                    {index !== (paper.authors || []).length - 1 && index % 2 === 1 && <br />}
                                </span>
                            ))}
                        </p>
                    </section>

                    <section className="paper-section">
                        <h2>ABSTRACT</h2>
                        <p className="paper-abstract">{paper.abstract}</p>
                    </section>

                    <div className="paper-stats">
                        <div>
                            <span className="stat-label">CITED BY</span>
                            <strong>{paper.citationCount}</strong>
                        </div>
                        <div>
                            <span className="stat-label">REFERENCES</span>
                            <strong>{paper.references}</strong>
                        </div>
                        <div>
                            <span className="stat-label">PDF</span>
                            <strong>
                                {paper.pdfUrl ? <a href={paper.pdfUrl} target="_blank" rel="noreferrer">DOWNLOAD</a> : "N/A"}
                            </strong>
                        </div>
                    </div>
                </div>

                <div className="paper-preview">
                    <div className="paper-preview-placeholder">
                        PAPER
                        <br />
                        PREVIEW
                    </div>
                </div>
            </section>
        </main>
    );
}

export default Paper;