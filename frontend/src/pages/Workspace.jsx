import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";

import {
    getPaperDetails,
    analyzePaper,
    askPaper,
    summarizePaper,
    extractPaperInfo,
    getResearchGaps,
    verifyCitations,
} from "../lib/api";

import "../styles/pages/workspace.css";

// ─────────────────────────────────────────────────────────────
// TAB IDs
// ─────────────────────────────────────────────────────────────
const TABS = {
    SUMMARY: "SUMMARY",
    INSIGHTS: "INSIGHTS",
    EXTRACT: "EXTRACT",
    CITATIONS: "CITATIONS",
};

function Workspace() {
    const { id } = useParams();

    // Paper state
    const [paper, setPaper] = useState(null);
    const [loadingPaper, setLoadingPaper] = useState(true);

    // RAG state
    const [isAnalyzed, setIsAnalyzed] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analyzeResult, setAnalyzeResult] = useState(null);
    const [analyzeError, setAnalyzeError] = useState(null);

    // Active tab
    const [activeTab, setActiveTab] = useState(TABS.SUMMARY);

    // Summary
    const [summary, setSummary] = useState(null);
    const [loadingSummary, setLoadingSummary] = useState(false);
    const [summaryError, setSummaryError] = useState(null);

    // Q&A
    const [question, setQuestion] = useState("");
    const [qaResult, setQaResult] = useState(null);
    const [loadingQa, setLoadingQa] = useState(false);
    const [qaError, setQaError] = useState(null);
    const textareaRef = useRef(null);

    // Extraction
    const [extractResult, setExtractResult] = useState(null);
    const [loadingExtract, setLoadingExtract] = useState(false);
    const [extractError, setExtractError] = useState(null);

    // Research Gaps (Insights tab)
    const [gapsResult, setGapsResult] = useState(null);
    const [loadingGaps, setLoadingGaps] = useState(false);
    const [gapsError, setGapsError] = useState(null);

    // Citation Verification
    const [verifyInput, setVerifyInput] = useState("");
    const [verifyResult, setVerifyResult] = useState(null);
    const [loadingVerify, setLoadingVerify] = useState(false);
    const [verifyError, setVerifyError] = useState(null);

    // ─────────────────────────────────────────────────────────
    // LOAD PAPER
    // ─────────────────────────────────────────────────────────

    useEffect(() => {
        if (!id) {
            setLoadingPaper(false);
            return;
        }

        async function load() {
            setLoadingPaper(true);
            setIsAnalyzed(false);
            setAnalyzeResult(null);
            setAnalyzeError(null);
            setSummary(null);
            setSummaryError(null);
            setExtractResult(null);
            setExtractError(null);
            setGapsResult(null);
            setGapsError(null);
            try {
                const data = await getPaperDetails(id);
                setPaper(data);
                setIsAnalyzed(data.status === "analyzed");
            } catch (err) {
                console.error(err);
            } finally {
                setLoadingPaper(false);
            }
        }

        load();
    }, [id]);

    // ─────────────────────────────────────────────────────────
    // ANALYZE
    // ─────────────────────────────────────────────────────────

    async function handleAnalyze() {
        if (!id) return;
        setIsAnalyzing(true);
        setAnalyzeError(null);
        setAnalyzeResult(null);

        try {
            const result = await analyzePaper(id);
            setAnalyzeResult(result);
            setIsAnalyzed(true);
        } catch (err) {
            setAnalyzeError(err.message);
        } finally {
            setIsAnalyzing(false);
        }
    }

    // ─────────────────────────────────────────────────────────
    // SUMMARIZE
    // ─────────────────────────────────────────────────────────

    async function handleSummarize() {
        if (!id || !isAnalyzed) return;
        setLoadingSummary(true);
        setSummaryError(null);

        try {
            const result = await summarizePaper(id);
            setSummary(result.summary);
            setActiveTab(TABS.SUMMARY);
        } catch (err) {
            setSummaryError(err.message);
        } finally {
            setLoadingSummary(false);
        }
    }

    // ─────────────────────────────────────────────────────────
    // Q&A
    // ─────────────────────────────────────────────────────────

    async function handleAsk() {
        if (!id || !isAnalyzed || !question.trim()) return;
        setLoadingQa(true);
        setQaError(null);
        setQaResult(null);

        try {
            const result = await askPaper(id, question.trim());
            setQaResult(result);
        } catch (err) {
            setQaError(err.message);
        } finally {
            setLoadingQa(false);
        }
    }

    function handleQuestionKeyDown(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleAsk();
        }
    }

    // ─────────────────────────────────────────────────────────
    // EXTRACT
    // ─────────────────────────────────────────────────────────

    async function handleExtract() {
        if (!id || !isAnalyzed) return;
        setLoadingExtract(true);
        setExtractError(null);

        try {
            const result = await extractPaperInfo(id);
            setExtractResult(result);
            setActiveTab(TABS.EXTRACT);
        } catch (err) {
            setExtractError(err.message);
        } finally {
            setLoadingExtract(false);
        }
    }

    // ─────────────────────────────────────────────────────────
    // RESEARCH GAPS
    // ─────────────────────────────────────────────────────────

    async function handleGaps() {
        if (!id || !isAnalyzed) return;
        setLoadingGaps(true);
        setGapsError(null);

        try {
            const result = await getResearchGaps(id);
            setGapsResult(result);
            setActiveTab(TABS.INSIGHTS);
        } catch (err) {
            setGapsError(err.message);
        } finally {
            setLoadingGaps(false);
        }
    }

    async function handleTabChange(tab) {
        setActiveTab(tab);

        if (!isAnalyzed) return;

        if (tab === TABS.SUMMARY && !summary && !loadingSummary) {
            await handleSummarize();
        } else if (tab === TABS.INSIGHTS && !gapsResult && !loadingGaps) {
            await handleGaps();
        } else if (tab === TABS.EXTRACT && !extractResult && !loadingExtract) {
            await handleExtract();
        }
    }

    // ─────────────────────────────────────────────────────────
    // CITATION VERIFY
    // ─────────────────────────────────────────────────────────

    async function handleVerify() {
        if (!id || !isAnalyzed || !verifyInput.trim()) return;
        setLoadingVerify(true);
        setVerifyError(null);
        setVerifyResult(null);

        try {
            const result = await verifyCitations(id, verifyInput.trim());
            setVerifyResult(result);
            setActiveTab(TABS.CITATIONS);
        } catch (err) {
            setVerifyError(err.message);
        } finally {
            setLoadingVerify(false);
        }
    }

    // ─────────────────────────────────────────────────────────
    // RENDER HELPERS
    // ─────────────────────────────────────────────────────────

    if (loadingPaper) {
        return (
            <main className="workspace-page">
                <Navbar />
                <div className="workspace-toolbar"><div className="workspace-paper-name">LOADING...</div></div>
            </main>
        );
    }

    if (!paper) {
        return (
            <main className="workspace-page">
                <Navbar />
                <div className="workspace-toolbar"><div className="workspace-paper-name">PAPER NOT FOUND</div></div>
            </main>
        );
    }

    let authors = [];
    if (Array.isArray(paper.authors)) {
        authors = paper.authors;
    } else if (typeof paper.authors === "string") {
        try {
            const parsed = JSON.parse(paper.authors);
            authors = Array.isArray(parsed) ? parsed : [paper.authors];
        } catch {
            authors = [paper.authors];
        }
    }

    return (
        <main className="workspace-page">
            <Navbar />

            {/* TOP BAR */}
            <div className="workspace-toolbar">
                <div className="workspace-paper-name">
                    PAPER : {paper.title?.toUpperCase()}
                </div>
            </div>

            {/* MAIN WORKSPACE */}
            <section className="workspace-layout">

                {/* LEFT SIDE — paper info + actions */}
                <aside className="workspace-paper">

                    <div className="workspace-label">PAPER</div>

                    <h1 className="workspace-title">{paper.title}</h1>

                    <div className="workspace-meta">
                        <span>{paper.year || "—"}</span>
                        <span>|</span>
                        <span>{paper.source || "—"}</span>
                    </div>

                    <section className="workspace-section">
                        <h2>AUTHORS</h2>
                        <p style={{ fontSize: "0.8rem", lineHeight: 1.6, opacity: 0.8 }}>
                            {authors.slice(0, 5).join(" · ") || "Unknown"}
                        </p>
                    </section>

                    <section className="workspace-section">
                        <h2>ABSTRACT</h2>
                        <p>{paper.abstract || "No abstract available."}</p>
                    </section>

                    {/* ANALYZE CONTROL */}
                    <section className="workspace-section">
                        <h2>ANALYSIS</h2>

                        {!isAnalyzed ? (
                            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                                <p style={{ fontSize: "0.75rem", opacity: 0.6 }}>
                                    Analyze this paper to enable Q&amp;A, summarization,
                                    and information extraction.
                                </p>
                                <button
                                    onClick={handleAnalyze}
                                    disabled={isAnalyzing}
                                    style={actionBtnStyle(isAnalyzing)}
                                >
                                    {isAnalyzing ? "ANALYZING..." : "ANALYZE PAPER"}
                                </button>
                                {analyzeError && (
                                    <p style={errorStyle}>{analyzeError}</p>
                                )}
                            </div>
                        ) : (
                            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                                <p style={{ fontSize: "0.75rem", color: "#4ade80" }}>
                                    ✓ PAPER ANALYZED
                                    {analyzeResult && (
                                        <> — {analyzeResult.chunks} CHUNKS / {analyzeResult.vectors} VECTORS</>
                                    )}
                                </p>

                                <button
                                    onClick={handleSummarize}
                                    disabled={loadingSummary}
                                    style={actionBtnStyle(loadingSummary)}
                                >
                                    {loadingSummary ? "SUMMARIZING..." : "SUMMARIZE"}
                                </button>

                                <button
                                    onClick={handleExtract}
                                    disabled={loadingExtract}
                                    style={actionBtnStyle(loadingExtract)}
                                >
                                    {loadingExtract ? "EXTRACTING..." : "EXTRACT INFO"}
                                </button>

                                <button
                                    onClick={handleGaps}
                                    disabled={loadingGaps}
                                    style={actionBtnStyle(loadingGaps)}
                                >
                                    {loadingGaps ? "DETECTING..." : "RESEARCH GAPS"}
                                </button>
                            </div>
                        )}
                    </section>

                    {/* PDF LINK */}
                    {paper.pdfUrl && (
                        <section className="workspace-section">
                            <h2>PDF</h2>
                            <a
                                href={paper.pdfUrl}
                                target="_blank"
                                rel="noreferrer"
                                style={{ fontSize: "0.75rem", opacity: 0.7 }}
                            >
                                OPEN PDF →
                            </a>
                        </section>
                    )}

                </aside>


                {/* RIGHT SIDE — AI results */}
                <section className="workspace-ai">

                    {/* TABS */}
                    <div className="workspace-tabs">
                        <button
                            className={activeTab === TABS.SUMMARY ? "active" : ""}
                            onClick={() => handleTabChange(TABS.SUMMARY)}
                        >
                            SUMMARY
                        </button>
                        <button
                            className={activeTab === TABS.INSIGHTS ? "active" : ""}
                            onClick={() => handleTabChange(TABS.INSIGHTS)}
                        >
                            INSIGHTS
                        </button>
                        <button
                            className={activeTab === TABS.EXTRACT ? "active" : ""}
                            onClick={() => handleTabChange(TABS.EXTRACT)}
                        >
                            EXTRACT
                        </button>
                        <button
                            className={activeTab === TABS.CITATIONS ? "active" : ""}
                            onClick={() => setActiveTab(TABS.CITATIONS)}
                        >
                            CITATIONS
                        </button>
                    </div>


                    {/* ── SUMMARY TAB ── */}
                    {activeTab === TABS.SUMMARY && (
                        <div className="workspace-summary">
                            {summaryError && <p style={errorStyle}>{summaryError}</p>}
                            {summary ? (
                                <pre style={{
                                    whiteSpace: "pre-wrap",
                                    fontFamily: "inherit",
                                    fontSize: "0.82rem",
                                    lineHeight: 1.7,
                                }}>
                                    {summary}
                                </pre>
                            ) : (
                                <p style={{ opacity: 0.5 }}>
                                    {isAnalyzed
                                        ? "Click SUMMARIZE to generate a structured paper summary."
                                        : "Analyze the paper first, then click SUMMARIZE."}
                                </p>
                            )}
                        </div>
                    )}


                    {/* ── INSIGHTS TAB (Research Gaps) ── */}
                    {activeTab === TABS.INSIGHTS && (
                        <div className="workspace-insights">
                            {gapsError && <p style={errorStyle}>{gapsError}</p>}

                            {gapsResult ? (
                                <>
                                    <GapSection title="RESEARCH GAPS" items={gapsResult.research_gaps} />
                                    <GapSection title="LIMITATIONS" items={gapsResult.limitations} />
                                    <GapSection title="UNRESOLVED QUESTIONS" items={gapsResult.unresolved_questions} />
                                    <GapSection title="FUTURE WORK" items={gapsResult.future_work} />
                                </>
                            ) : (
                                <p style={{ opacity: 0.5 }}>
                                    {loadingGaps
                                        ? "Detecting research gaps..."
                                        : isAnalyzed
                                        ? "Click RESEARCH GAPS to detect limitations and open questions."
                                        : "Analyze the paper first."}
                                </p>
                            )}
                        </div>
                    )}


                    {/* ── EXTRACT TAB ── */}
                    {activeTab === TABS.EXTRACT && (
                        <div className="workspace-insights">
                            {extractError && <p style={errorStyle}>{extractError}</p>}

                            {extractResult ? (
                                <>
                                    <ExtractSection title="MODELS" items={extractResult.models} />
                                    <ExtractSection title="DATASETS" items={extractResult.datasets} />
                                    <ExtractSection title="METRICS" items={extractResult.metrics} />
                                    <ExtractSection title="KEY RESULTS" items={extractResult.results} />
                                    <ExtractSection title="METHODS" items={extractResult.methods} />
                                    <ExtractSection title="EXPERIMENTAL SETTINGS" items={extractResult.experimental_settings} />
                                </>
                            ) : (
                                <p style={{ opacity: 0.5 }}>
                                    {loadingExtract
                                        ? "Extracting paper information..."
                                        : isAnalyzed
                                        ? "Click EXTRACT INFO to extract structured information."
                                        : "Analyze the paper first."}
                                </p>
                            )}
                        </div>
                    )}


                    {/* ── CITATIONS TAB ── */}
                    {activeTab === TABS.CITATIONS && (
                        <div className="workspace-insights">
                            <div style={{ marginBottom: "1rem" }}>
                                <label style={{ fontSize: "0.7rem", letterSpacing: "0.1em", opacity: 0.6 }}>
                                    CLAIM TO VERIFY
                                </label>
                                <textarea
                                    value={verifyInput}
                                    onChange={(e) => setVerifyInput(e.target.value)}
                                    placeholder="> paste a claim or answer to verify against the paper..."
                                    style={{
                                        width: "100%",
                                        minHeight: "80px",
                                        background: "transparent",
                                        border: "1px solid rgba(255,255,255,0.2)",
                                        color: "inherit",
                                        padding: "0.5rem",
                                        fontFamily: "inherit",
                                        fontSize: "0.8rem",
                                        resize: "vertical",
                                        marginTop: "0.5rem",
                                    }}
                                />
                                <button
                                    onClick={handleVerify}
                                    disabled={loadingVerify || !verifyInput.trim() || !isAnalyzed}
                                    style={{ ...actionBtnStyle(loadingVerify), marginTop: "0.5rem" }}
                                >
                                    {loadingVerify ? "VERIFYING..." : "VERIFY CITATIONS"}
                                </button>
                            </div>

                            {verifyError && <p style={errorStyle}>{verifyError}</p>}

                            {verifyResult && (
                                <div>
                                    <p style={{
                                        color: verifyResult.verified ? "#4ade80" : "#f87171",
                                        fontSize: "0.75rem",
                                        marginBottom: "1rem",
                                    }}>
                                        {verifyResult.verified ? "✓ VERIFIED" : "✗ NOT FULLY VERIFIED"}
                                    </p>

                                    {(verifyResult.claims || []).map((claim, i) => (
                                        <div key={i} style={{
                                            background: "rgba(255,255,255,0.04)",
                                            border: "1px solid rgba(255,255,255,0.1)",
                                            padding: "0.75rem",
                                            marginBottom: "0.75rem",
                                        }}>
                                            <p style={{ fontSize: "0.8rem", fontWeight: 600 }}>
                                                {claim.supported ? "✓" : "✗"} {claim.claim}
                                            </p>
                                            <p style={{ fontSize: "0.75rem", opacity: 0.7, marginTop: "0.4rem" }}>
                                                {claim.reason}
                                            </p>
                                            {claim.sources?.length > 0 && (
                                                <p style={{ fontSize: "0.7rem", opacity: 0.5, marginTop: "0.4rem" }}>
                                                    SOURCES: {claim.sources.join(", ")}
                                                </p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}

                            {!verifyResult && !verifyError && (
                                <p style={{ opacity: 0.5 }}>
                                    {isAnalyzed
                                        ? "Enter a claim above and click VERIFY CITATIONS."
                                        : "Analyze the paper first."}
                                </p>
                            )}
                        </div>
                    )}


                    {/* ── QUERY (always visible below tabs) ── */}
                    <div className="workspace-query">
                        <label>QUERY</label>

                        <textarea
                            ref={textareaRef}
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onKeyDown={handleQuestionKeyDown}
                            placeholder="> ask something about this paper..."
                            disabled={!isAnalyzed || loadingQa}
                        />

                        <div className="workspace-query-hint">
                            ENTER TO SEND
                            <br />
                            SHIFT + ENTER FOR NEW LINE
                        </div>

                        {isAnalyzed && question.trim() && (
                            <button
                                onClick={handleAsk}
                                disabled={loadingQa}
                                style={{ ...actionBtnStyle(loadingQa), marginTop: "0.5rem" }}
                            >
                                {loadingQa ? "THINKING..." : "ASK →"}
                            </button>
                        )}

                        {!isAnalyzed && (
                            <p style={{ fontSize: "0.7rem", opacity: 0.4, marginTop: "0.5rem" }}>
                                ANALYZE PAPER TO ENABLE Q&A
                            </p>
                        )}
                    </div>

                    {/* Q&A RESULT */}
                    {qaError && <p style={{ ...errorStyle, margin: "0 0 1rem 0" }}>{qaError}</p>}

                    {qaResult && (
                        <div style={{
                            background: "rgba(255,255,255,0.04)",
                            border: "1px solid rgba(255,255,255,0.1)",
                            padding: "1rem",
                            margin: "0.5rem 0 1rem 0",
                        }}>
                            <p style={{ fontSize: "0.7rem", opacity: 0.5, marginBottom: "0.5rem" }}>
                                ANSWER
                            </p>
                            <p style={{ fontSize: "0.85rem", lineHeight: 1.7 }}>
                                {qaResult.answer}
                            </p>

                            {qaResult.sources?.length > 0 && (
                                <div style={{ marginTop: "1rem" }}>
                                    <p style={{ fontSize: "0.65rem", opacity: 0.5, marginBottom: "0.5rem" }}>
                                        SOURCES ({qaResult.sources.length})
                                    </p>
                                    {qaResult.sources.map((src, i) => (
                                        <div key={i} style={{
                                            fontSize: "0.72rem",
                                            opacity: 0.65,
                                            borderTop: "1px solid rgba(255,255,255,0.08)",
                                            paddingTop: "0.5rem",
                                            marginTop: "0.5rem",
                                        }}>
                                            <strong>{src.chunk_id}</strong>
                                            {src.section && <> · {src.section}</>}
                                            {src.page_start != null && <> · P.{src.page_start}</>}
                                            <> · score {src.score}</>
                                            <br />
                                            <span style={{ opacity: 0.6 }}>{src.text}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                </section>

            </section>
        </main>
    );
}

// ─────────────────────────────────────────────────────────────
// SUB-COMPONENTS
// ─────────────────────────────────────────────────────────────

function GapSection({ title, items }) {
    if (!items?.length) return null;
    return (
        <div className="insight-card">
            <h3>{title}</h3>
            <ul style={{ paddingLeft: "1.2rem", lineHeight: 1.7, fontSize: "0.82rem" }}>
                {items.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
        </div>
    );
}

function ExtractSection({ title, items }) {
    if (!items?.length) return null;
    return (
        <div className="insight-card">
            <h3>{title}</h3>
            <ul style={{ paddingLeft: "1.2rem", lineHeight: 1.7, fontSize: "0.82rem" }}>
                {items.map((item, i) => (
                    <li key={i}>{typeof item === "object" ? JSON.stringify(item) : item}</li>
                ))}
            </ul>
        </div>
    );
}

// ─────────────────────────────────────────────────────────────
// STYLES
// ─────────────────────────────────────────────────────────────

function actionBtnStyle(disabled) {
    return {
        background: "transparent",
        border: "1px solid currentColor",
        color: "inherit",
        padding: "0.4rem 1rem",
        fontSize: "0.72rem",
        letterSpacing: "0.12em",
        cursor: disabled ? "wait" : "pointer",
        opacity: disabled ? 0.5 : 1,
        fontFamily: "inherit",
    };
}

const errorStyle = {
    color: "#f87171",
    fontSize: "0.75rem",
    background: "rgba(248,113,113,0.1)",
    padding: "0.5rem",
    border: "1px solid rgba(248,113,113,0.3)",
};

export default Workspace;
