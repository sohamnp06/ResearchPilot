import { useEffect, useState, useCallback } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";
import SortBar from "../components/SortBar/SortBar";
import { searchPapersExternal, importPaper } from "../lib/api";
import PaperCard from "../components/PaperCard/PaperCard";

import "../styles/pages/search.css";

function Search() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const query = searchParams.get("q") || "transformer";
    const [results, setResults] = useState([]);
    const [similarPapers, setSimilarPapers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [hasExactMatch, setHasExactMatch] = useState(true);
    const [importingId, setImportingId] = useState(null);

    const loadResults = useCallback(async () => {
        setLoading(true);
        setError(null);
        setResults([]);
        setSimilarPapers([]);

        try {
            const data = await searchPapersExternal(query, 10);
            setResults(data.results || []);
            setSimilarPapers(data.similar_papers || []);
            setHasExactMatch(data.has_exact_match !== false);
        } catch (err) {
            console.error(err);
            setError(err.message || "Search failed. Please try again.");
        } finally {
            setLoading(false);
        }
    }, [query]);

    useEffect(() => {
        loadResults();
    }, [loadResults]);

    async function handleOpenPaper(paper) {
        setImportingId(paper.paper_id);
        try {
            const imported = await importPaper({
                paper_id: paper.paper_id,
                title: paper.title,
                abstract: paper.abstract,
                authors: paper.authors,
                year: paper.year,
                citation_count: paper.citation_count,
                pdf_url: paper.pdf_url,
                source: paper.source,
            });
            navigate(`/paper/${imported.id}`);
        } catch (err) {
            console.error(err);
            alert("Could not open this paper: " + err.message);
        } finally {
            setImportingId(null);
        }
    }

    const totalFound = results.length + similarPapers.length;

    return (
        <main className="search-page">
            <Navbar />

            <div className="search-header">
                <BackButton />
                <SortBar />
            </div>

            <section className={`search-status ${loading ? "is-loading" : "is-loaded"}`}>
                {loading ? (
                    <>
                        <h1>SEARCHING ARCHIVE<span className="search-dots">...</span></h1>
                        <p>SEARCHING SEMANTIC SCHOLAR</p>
                    </>
                ) : error ? (
                    <>
                        <h1>SEARCH ERROR</h1>
                        <p>{error}</p>
                    </>
                ) : (
                    <>
                        <h1>ARCHIVE RESULTS</h1>
                        <p>{totalFound} PAPERS FOUND FOR "{query}"</p>
                    </>
                )}
            </section>

            {!loading && !error && (
                <>
                    {/* EXACT / PRIMARY RESULTS */}
                    {results.length > 0 && (
                        <section className="paper-list">
                            {results.map((paper,index) => (
                                <PaperCard
                                    key={paper.paper_id}
                                    paper={paper}
                                    displayId={`RP-${String(index + 1).padStart(3, "0")}`}
                                    onOpen={handleOpenPaper}
                                    importing={importingId === paper.paper_id}
                                />
                            ))}
                        </section>
                    )}

                    {/* SIMILAR PAPERS — shown when no exact match */}
                    {!hasExactMatch && similarPapers.length > 0 && (
                        <>
                            <section className="search-status is-loaded" style={{ marginTop: "2rem" }}>
                                <h1>SIMILAR PAPERS</h1>
                                <p>NO EXACT MATCH FOUND — DID YOU MEAN ONE OF THESE?</p>
                            </section>

                            <section className="paper-list">
                                {similarPapers.map((paper,index) => (
                                    <PaperCard
                                        key={paper.paper_id}
                                        paper={paper}
                                        displayId={`RP-${String(index + 1).padStart(3, "0")}`}
                                        onOpen={handleOpenPaper}
                                        importing={importingId === paper.paper_id}
                                        isSimilar
                                    />
                                ))}
                            </section>
                        </>
                    )}

                    {/* NO RESULTS AT ALL */}
                    {totalFound === 0 && (
                        <section className="paper-list">
                            <p style={{ padding: "2rem", opacity: 0.6 }}>
                                NO PAPERS FOUND FOR "{query}". TRY A DIFFERENT SEARCH TERM.
                            </p>
                        </section>
                    )}
                </>
            )}
        </main>
    );
}

export default Search;