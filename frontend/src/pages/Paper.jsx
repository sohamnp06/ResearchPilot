import { useEffect, useState, useRef } from "react";
import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";
import { useNavigate, useParams } from "react-router-dom";
import { addToLibrary, getPaperDetails } from "../lib/api";
import { Document, Page, pdfjs } from "react-pdf";

import "../styles/pages/paper.css";

pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

function FirstPagePreview({ file, title }) {
    const containerRef = useRef(null);
    const [pageWidth, setPageWidth] = useState(400);
    const [loadError, setLoadError] = useState(false);

    useEffect(() => {
        function updateWidth() {
            if (!containerRef.current) return;
            const width = containerRef.current.clientWidth;
            setPageWidth(Math.max(width - 24, 260));
        }

        updateWidth();
        const observer = new ResizeObserver(updateWidth);
        if (containerRef.current) {
            observer.observe(containerRef.current);
        }
        return () => observer.disconnect();
    }, []);

    if (!file) {
        return (
            <div className="paper-preview-placeholder">
                <span>NO PDF AVAILABLE</span>
                <span style={{ fontSize: "12px", opacity: 0.6, marginTop: "8px" }}>
                    PREVIEW CANNOT BE LOADED
                </span>
            </div>
        );
    }

    return (
        <div className="paper-preview-container" ref={containerRef}>
            <div className="paper-preview-header">
                <span>PREVIEW · FIRST PAGE</span>
            </div>
            <div className="paper-preview-body">
                <Document
                    file={file}
                    onLoadError={(err) => {
                        console.error("PDF preview error:", err);
                        setLoadError(true);
                    }}
                    loading={
                        <div className="paper-preview-loading">
                            LOADING FIRST PAGE...
                        </div>
                    }
                    error={
                        <div className="paper-preview-error">
                            <span>COULD NOT RENDER PDF PREVIEW</span>
                            <span style={{ fontSize: "11px", opacity: 0.6 }}>
                                {title}
                            </span>
                        </div>
                    }
                >
                    {!loadError && (
                        <>
                            <Page
                                pageNumber={1}
                                width={pageWidth}
                                renderTextLayer={false}
                                renderAnnotationLayer={false}
                            />
                            {file && (
                                <object
                                    data={file}
                                    type="application/pdf"
                                    width="100%"
                                    height="500px"
                                    style={{ display: "none" }}
                                >
                                    <embed src={file} type="application/pdf" />
                                </object>
                            )}
                        </>
                    )}
                </Document>
            </div>
        </div>
    );
}

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

    const pdfUrl = paper.pdfUrl ? String(paper.pdfUrl).trim() : null;

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
                    <FirstPagePreview file={pdfUrl} title={paper.title} />
                </div>
            </section>
        </main>
    );
}

export default Paper;