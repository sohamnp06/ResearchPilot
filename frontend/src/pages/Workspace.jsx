import { useEffect, useState, useRef, useCallback } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";

import {
    getPaperDetails,
    analyzePaper,
    askPaper,
    summarizePaper,
    getResearchGaps,
} from "../lib/api";

import "../styles/pages/workspace.css";

// ─────────────────────────────────────────────────────────────
// TAB IDs (4 inline tabs)
// ─────────────────────────────────────────────────────────────
const TABS = {
    SUMMARY: "SUMMARY",
    INSIGHTS: "INSIGHTS",
    GAPS: "RESEARCH GAPS",
    CHAT: "CHAT",
};

// ─────────────────────────────────────────────────────────────
// HELPER: PARSE SUMMARY INTO BRIEF SECTION INSIGHTS
// ─────────────────────────────────────────────────────────────
function parseSummarySections(summaryText) {
    if (!summaryText) return [];

    const lines = summaryText.split("\n");
    const sections = [];
    let currentTitle = "OVERVIEW";
    let currentLines = [];

    const headerRegex = /^(?:\d+[\.\)]\s+|\#{1,4}\s+|\*\*)([A-Za-z\s\/&]+?)(?:\*\*|:|\s*\(.*?\))?$/;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const match = line.match(headerRegex);
        const isCommonHeader = /^(research problem|objective|methodology|methods|experiments|dataset|datasets|key results|results|main findings|findings|limitations|conclusion|future work)/i.test(line.replace(/^[\d\.\#\*\-\s]+/, ""));

        if ((match && isCommonHeader) || (line.startsWith("1.") || line.startsWith("2.") || line.startsWith("3.") || line.startsWith("4.") || line.startsWith("5.") || line.startsWith("6.") || line.startsWith("7.") || line.startsWith("8."))) {
            if (currentLines.length > 0) {
                const text = currentLines.join("\n").trim();
                if (text) {
                    sections.push({
                        title: currentTitle.replace(/^\d+[\.\)]\s*/, "").toUpperCase(),
                        content: text,
                    });
                }
                currentLines = [];
            }
            currentTitle = line.replace(/^[\d\.\#\*\-\s]+/, "").replace(/[\*:]+$/, "").trim();
        } else {
            currentLines.push(lines[i]);
        }
    }

    if (currentLines.length > 0) {
        const text = currentLines.join("\n").trim();
        if (text) {
            sections.push({
                title: currentTitle.replace(/^\d+[\.\)]\s*/, "").toUpperCase(),
                content: text,
            });
        }
    }

    if (sections.length === 0 && summaryText.trim()) {
        return [
            {
                title: "SUMMARY & OVERVIEW",
                content: summaryText.trim(),
            },
        ];
    }

    return sections;
}

function Workspace() {
    const { id } = useParams();

    // Paper state
    const [paper, setPaper] = useState(null);
    const [loadingPaper, setLoadingPaper] = useState(true);

    // RAG analysis state
    const [isAnalyzed, setIsAnalyzed] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analyzeResult, setAnalyzeResult] = useState(null);
    const [analyzeError, setAnalyzeError] = useState(null);

    // Active tab
    const [activeTab, setActiveTab] = useState(TABS.SUMMARY);

    // Summary state
    const [summary, setSummary] = useState(null);
    const [loadingSummary, setLoadingSummary] = useState(false);
    const [summaryError, setSummaryError] = useState(null);

    // Research Gaps state
    const [gapsResult, setGapsResult] = useState(null);
    const [loadingGaps, setLoadingGaps] = useState(false);
    const [gapsError, setGapsError] = useState(null);

    // Chat / Q&A state
    const [question, setQuestion] = useState("");
    const [chatHistory, setChatHistory] = useState([]);
    const [loadingQa, setLoadingQa] = useState(false);
    const [qaError, setQaError] = useState(null);
    const textareaRef = useRef(null);
    const chatContainerRef = useRef(null);

    useEffect(() => {
        if (chatHistory.length > 0 && chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [chatHistory, loadingQa]);

    // ─────────────────────────────────────────────────────────
    // AUTO-LOAD SUMMARY
    // ─────────────────────────────────────────────────────────
    const loadSummaryForPaper = useCallback(async (paperId) => {
        if (!paperId) return;
        setLoadingSummary(true);
        setSummaryError(null);

        try {
            const result = await summarizePaper(paperId);
            setSummary(result.summary);
        } catch (err) {
            console.error("Summary error:", err);
            setSummaryError(err.message || "Failed to generate summary.");
        } finally {
            setLoadingSummary(false);
        }
    }, []);

    // ─────────────────────────────────────────────────────────
    // TRIGGER ANALYSIS & AUTO-SUMMARIZE
    // ─────────────────────────────────────────────────────────
    const triggerAnalysis = useCallback(async (paperId) => {
        if (!paperId) return;
        setIsAnalyzing(true);
        setAnalyzeError(null);
        setAnalyzeResult(null);

        try {
            const result = await analyzePaper(paperId);
            setAnalyzeResult(result);
            setIsAnalyzed(true);
            await loadSummaryForPaper(paperId);
        } catch (err) {
            console.error("Analysis error:", err);
            setAnalyzeError(err.message || "Failed to analyze paper.");
        } finally {
            setIsAnalyzing(false);
        }
    }, [loadSummaryForPaper]);

    // ─────────────────────────────────────────────────────────
    // LOAD PAPER & AUTO-START ANALYSIS ON OPENING WORKSPACE
    // ─────────────────────────────────────────────────────────
    useEffect(() => {
        if (!id) {
            setLoadingPaper(false);
            return;
        }

        let isMounted = true;

        async function load() {
            setLoadingPaper(true);
            setIsAnalyzed(false);
            setIsAnalyzing(false);
            setAnalyzeResult(null);
            setAnalyzeError(null);
            setSummary(null);
            setSummaryError(null);
            setGapsResult(null);
            setGapsError(null);
            setChatHistory([]);

            try {
                const data = await getPaperDetails(id);
                if (!isMounted) return;
                setPaper(data);

                if (data.status === "analyzed") {
                    setIsAnalyzed(true);
                    loadSummaryForPaper(id);
                } else {
                    triggerAnalysis(id);
                }
            } catch (err) {
                console.error("Error loading paper details:", err);
                if (isMounted) {
                    setAnalyzeError(err.message || "Could not load paper.");
                }
            } finally {
                if (isMounted) {
                    setLoadingPaper(false);
                }
            }
        }

        load();

        return () => {
            isMounted = false;
        };
    }, [id, loadSummaryForPaper, triggerAnalysis]);

    // ─────────────────────────────────────────────────────────
    // LOAD RESEARCH GAPS
    // ─────────────────────────────────────────────────────────
    const loadGapsForPaper = useCallback(async (paperId) => {
        if (!paperId) return;
        setLoadingGaps(true);
        setGapsError(null);

        try {
            const result = await getResearchGaps(paperId);
            setGapsResult(result);
        } catch (err) {
            console.error("Research gaps error:", err);
            setGapsError(err.message || "Failed to detect research gaps.");
        } finally {
            setLoadingGaps(false);
        }
    }, []);

    // ─────────────────────────────────────────────────────────
    // TAB CHANGE HANDLER
    // ─────────────────────────────────────────────────────────
    async function handleTabChange(tab) {
        setActiveTab(tab);

        if (!isAnalyzed) return;

        if (tab === TABS.SUMMARY && !summary && !loadingSummary) {
            await loadSummaryForPaper(id);
        } else if (tab === TABS.INSIGHTS && !summary && !loadingSummary) {
            await loadSummaryForPaper(id);
        } else if (tab === TABS.GAPS && !gapsResult && !loadingGaps) {
            await loadGapsForPaper(id);
        }
    }

    // ─────────────────────────────────────────────────────────
    // CHAT / Q&A
    // ─────────────────────────────────────────────────────────
    async function handleAskQuestion(queryToAsk) {
        const textToQuery = (queryToAsk || question).trim();
        if (!id || !isAnalyzed || !textToQuery || loadingQa) return;

        const userMsg = {
            id: Date.now(),
            role: "user",
            text: textToQuery,
        };

        setChatHistory((prev) => [...prev, userMsg]);
        setQuestion("");
        setLoadingQa(true);
        setQaError(null);

        try {
            const result = await askPaper(id, textToQuery);
            const assistantMsg = {
                id: Date.now() + 1,
                role: "assistant",
                text: result.answer,
                sources: result.sources || [],
            };
            setChatHistory((prev) => [...prev, assistantMsg]);
        } catch (err) {
            setQaError(err.message || "Failed to get answer.");
        } finally {
            setLoadingQa(false);
        }
    }

    function handleQuestionKeyDown(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleAskQuestion();
        }
    }

    // ─────────────────────────────────────────────────────────
    // RENDER HELPERS
    // ─────────────────────────────────────────────────────────
    if (loadingPaper) {
        return (
            <main className="workspace-page">
                <Navbar />
                <div className="workspace-toolbar">
                    <div className="workspace-paper-name">LOADING WORKSPACE...</div>
                </div>
            </main>
        );
    }

    if (!paper) {
        return (
            <main className="workspace-page">
                <Navbar />
                <div className="workspace-toolbar">
                    <div className="workspace-paper-name">PAPER NOT FOUND</div>
                </div>
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

    const sectionInsights = parseSummarySections(summary);

    return (
        <main className="workspace-page">
            <Navbar />

            {/* TOP BAR */}
            <div className="workspace-toolbar">
                <BackButton />
                <div className="workspace-paper-name">
                    PAPER : {paper.title?.toUpperCase()}
                </div>
            </div>

            {/* MAIN WORKSPACE */}
            <section className="workspace-layout">

                {/* LEFT SIDE — Paper Info + Analysis Status */}
                <aside className="workspace-paper">
                    <div className="workspace-label">WORKSPACE</div>

                    <h1 className="workspace-title">{paper.title}</h1>

                    <div className="workspace-meta">
                        <span>{paper.displayId || paper.display_id || "PAPER"}</span>
                        <span>|</span>
                        <span>{paper.year || "—"}</span>
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

                    {/* LIVE ANALYSIS STATUS BADGE (Replaces old buttons) */}
                    <section className="workspace-section">
                        <h2>ANALYSIS STATUS</h2>

                        {isAnalyzing && (
                            <div className="analysis-status-card is-analyzing">
                                <div className="status-spinner-row">
                                    <span className="pulse-dot"></span>
                                    <strong style={{ letterSpacing: "0.08em" }}>ANALYZING PAPER...</strong>
                                </div>
                                <p style={{ fontSize: "0.75rem", opacity: 0.7, marginTop: "0.4rem" }}>
                                    Extracting text, generating semantic chunks, and building FAISS vector index.
                                </p>
                            </div>
                        )}

                        {isAnalyzed && !isAnalyzing && (
                            <div className="analysis-status-card is-ready">
                                <strong style={{ color: "#16a34a", letterSpacing: "0.08em" }}>
                                    ✓ PAPER ANALYZED
                                </strong>
                                <p style={{ fontSize: "0.75rem", opacity: 0.7, marginTop: "0.4rem" }}>
                                    {analyzeResult?.chunks
                                        ? `${analyzeResult.chunks} CHUNKS · ${analyzeResult.vectors || analyzeResult.chunks} VECTORS INDEXED`
                                        : "RAG index active & ready for Q&A, summary and insights."}
                                </p>
                            </div>
                        )}

                        {analyzeError && !isAnalyzing && (
                            <div className="analysis-status-card is-error">
                                <strong style={{ color: "#dc2626" }}>ANALYSIS FAILED</strong>
                                <p style={errorStyle}>{analyzeError}</p>
                                <button
                                    onClick={() => triggerAnalysis(id)}
                                    style={{ ...actionBtnStyle(false), marginTop: "0.6rem" }}
                                >
                                    RETRY ANALYSIS
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
                                style={{ fontSize: "0.75rem", opacity: 0.7, textDecoration: "underline" }}
                            >
                                OPEN FULL PDF →
                            </a>
                        </section>
                    )}
                </aside>

                {/* RIGHT SIDE — AI Tabs Panel */}
                <section className="workspace-ai">

                    {/* 4 INLINE TABS */}
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
                            className={activeTab === TABS.GAPS ? "active" : ""}
                            onClick={() => handleTabChange(TABS.GAPS)}
                        >
                            RESEARCH GAPS
                        </button>
                        <button
                            className={activeTab === TABS.CHAT ? "active" : ""}
                            onClick={() => handleTabChange(TABS.CHAT)}
                        >
                            CHAT
                        </button>
                    </div>

                    {/* ── 1. SUMMARY TAB (Summary and Overview) ── */}
                    {activeTab === TABS.SUMMARY && (
                        <div className="workspace-tab-content">
                            {summaryError && <p style={errorStyle}>{summaryError}</p>}

                            {loadingSummary ? (
                                <div className="workspace-loading-box">
                                    <span className="pulse-dot"></span>
                                    <p>GENERATING STRUCTURED SUMMARY &amp; OVERVIEW...</p>
                                </div>
                            ) : summary ? (
                                <div className="workspace-summary-view">
                                    <div className="summary-overview-badge">
                                        OVERVIEW &amp; STRUCTURED SUMMARY
                                    </div>
                                    <pre className="summary-text-block">
                                        {summary}
                                    </pre>
                                </div>
                            ) : (
                                <div className="workspace-empty-box">
                                    <p>
                                        {isAnalyzing
                                            ? "Analyzing paper and preparing summary..."
                                            : isAnalyzed
                                            ? "Summary not yet generated."
                                            : "Analyzing paper..."}
                                    </p>
                                    {isAnalyzed && (
                                        <button
                                            onClick={() => loadSummaryForPaper(id)}
                                            style={{ ...actionBtnStyle(false), marginTop: "1rem" }}
                                        >
                                            GENERATE SUMMARY
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── 2. INSIGHTS TAB (Sections in summary explained in brief) ── */}
                    {activeTab === TABS.INSIGHTS && (
                        <div className="workspace-tab-content">
                            {summaryError && <p style={errorStyle}>{summaryError}</p>}

                            {loadingSummary ? (
                                <div className="workspace-loading-box">
                                    <span className="pulse-dot"></span>
                                    <p>EXTRACTING SECTION INSIGHTS IN BRIEF...</p>
                                </div>
                            ) : sectionInsights.length > 0 ? (
                                <div className="workspace-insights-list">
                                    <div className="insights-header-note">
                                        <span>KEY SECTION BREAKDOWN &amp; BRIEF EXPLANATIONS</span>
                                    </div>
                                    {sectionInsights.map((sec, idx) => (
                                        <div key={idx} className="insight-card">
                                            <h3>{sec.title}</h3>
                                            <p style={{ whiteSpace: "pre-wrap" }}>{sec.content}</p>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="workspace-empty-box">
                                    <p>
                                        {isAnalyzing
                                            ? "Analyzing paper..."
                                            : "No section insights available yet."}
                                    </p>
                                    {isAnalyzed && (
                                        <button
                                            onClick={() => loadSummaryForPaper(id)}
                                            style={{ ...actionBtnStyle(false), marginTop: "1rem" }}
                                        >
                                            LOAD SECTION INSIGHTS
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── 3. RESEARCH GAPS TAB (Limitations, Future Work, Gaps) ── */}
                    {activeTab === TABS.GAPS && (
                        <div className="workspace-tab-content">
                            {gapsError && <p style={errorStyle}>{gapsError}</p>}

                            {loadingGaps ? (
                                <div className="workspace-loading-box">
                                    <span className="pulse-dot"></span>
                                    <p>DETECTING RESEARCH GAPS, LIMITATIONS &amp; FUTURE WORK...</p>
                                </div>
                            ) : gapsResult ? (
                                <div className="workspace-insights-list">
                                    <GapSection
                                        title="RESEARCH GAPS"
                                        items={gapsResult.research_gaps}
                                        description="Open gaps and unexplored challenges in the current literature."
                                    />
                                    <GapSection
                                        title="RESEARCH LIMITATIONS"
                                        items={gapsResult.limitations}
                                        description="Methodological, data, scale, or design constraints identified in this work."
                                    />
                                    <GapSection
                                        title="FUTURE WORK &amp; OPPORTUNITIES"
                                        items={gapsResult.future_work}
                                        description="Promising research directions, extensions, and next steps that can be done."
                                    />
                                    <GapSection
                                        title="UNRESOLVED QUESTIONS"
                                        items={gapsResult.unresolved_questions}
                                        description="Open questions left unanswered for subsequent investigation."
                                    />
                                </div>
                            ) : (
                                <div className="workspace-empty-box">
                                    <p>
                                        {isAnalyzing
                                            ? "Analyzing paper..."
                                            : isAnalyzed
                                            ? "Click below to detect research gaps, limitations, and future work."
                                            : "Paper analysis in progress..."}
                                    </p>
                                    {isAnalyzed && (
                                        <button
                                            onClick={() => loadGapsForPaper(id)}
                                            style={{ ...actionBtnStyle(false), marginTop: "1rem" }}
                                        >
                                            DETECT RESEARCH GAPS
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── 4. CHAT TAB (Q&A inline with other 3 tabs) ── */}
                    {activeTab === TABS.CHAT && (
                        <div className="workspace-tab-content workspace-chat-tab">
                            {/* IF NO QUESTIONS ASKED YET: SHOW INPUT AT TOP WITH SUGGESTED QUESTIONS */}
                            {chatHistory.length === 0 && (
                                <>
                                    <div className="workspace-query">
                                        <label>ASK A QUESTION</label>
                                        <textarea
                                            ref={textareaRef}
                                            value={question}
                                            onChange={(e) => setQuestion(e.target.value)}
                                            onKeyDown={handleQuestionKeyDown}
                                            placeholder={
                                                isAnalyzing
                                                    ? "Analyzing paper in progress..."
                                                    : isAnalyzed
                                                    ? "> ask anything about methodology, results, equations, or datasets..."
                                                    : "Please wait for paper analysis to complete..."
                                            }
                                            disabled={!isAnalyzed || loadingQa || isAnalyzing}
                                        />
                                        <div className="workspace-query-hint">
                                            ENTER TO SEND <br /> SHIFT + ENTER FOR NEW LINE
                                        </div>
                                        {isAnalyzed && question.trim() && (
                                            <button
                                                onClick={() => handleAskQuestion()}
                                                disabled={loadingQa}
                                                style={{ ...actionBtnStyle(loadingQa), marginTop: "0.6rem" }}
                                            >
                                                {loadingQa ? "SEARCHING..." : "ASK →"}
                                            </button>
                                        )}
                                    </div>

                                    {isAnalyzed && (
                                        <div className="prompt-chips" style={{ marginTop: "1rem" }}>
                                            <span style={{ fontSize: "0.7rem", opacity: 0.5, width: "100%", marginBottom: "4px" }}>
                                                SUGGESTED QUESTIONS:
                                            </span>
                                            <button
                                                className="prompt-chip"
                                                onClick={() => handleAskQuestion("What is the core contribution and architecture introduced in this paper?")}
                                            >
                                                What is the core contribution and architecture?
                                            </button>
                                            <button
                                                className="prompt-chip"
                                                onClick={() => handleAskQuestion("What datasets and evaluation benchmarks were used?")}
                                            >
                                                What datasets and benchmarks were used?
                                            </button>
                                            <button
                                                className="prompt-chip"
                                                onClick={() => handleAskQuestion("What are the key limitations and trade-offs of this approach?")}
                                            >
                                                What are the key limitations and trade-offs?
                                            </button>
                                        </div>
                                    )}
                                </>
                            )}

                            {/* CONVERSATION HISTORY */}
                            {chatHistory.length > 0 && (
                                <div className="chat-messages-container" ref={chatContainerRef}>
                                    {chatHistory.map((msg) => (
                                        <div
                                            key={msg.id}
                                            className={`chat-message ${msg.role === "user" ? "chat-msg-user" : "chat-msg-assistant"}`}
                                        >
                                            <div className="chat-msg-sender">
                                                {msg.role === "user" ? "> YOU" : "> RESEARCHPILOT AI"}
                                            </div>
                                            <div className="chat-msg-body">
                                                {msg.text}
                                            </div>
                                        </div>
                                    ))}

                                    {loadingQa && (
                                        <div className="chat-message chat-msg-assistant">
                                            <div className="chat-msg-sender">&gt; RESEARCHPILOT AI</div>
                                            <div className="chat-msg-body" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                                <span className="pulse-dot"></span>
                                                <span>Searching index &amp; generating grounded answer...</span>
                                            </div>
                                        </div>
                                    )}

                                    {qaError && (
                                        <div className="chat-error-banner">
                                            {qaError}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* IF QUESTIONS HAVE BEEN ASKED: MOVE CHAT INPUT TO THE BOTTOM */}
                            {chatHistory.length > 0 && (
                                <div className="workspace-query">
                                    <label>ASK A QUESTION</label>
                                    <textarea
                                        ref={textareaRef}
                                        value={question}
                                        onChange={(e) => setQuestion(e.target.value)}
                                        onKeyDown={handleQuestionKeyDown}
                                        placeholder={
                                            isAnalyzing
                                                ? "Analyzing paper in progress..."
                                                : isAnalyzed
                                                ? "> ask anything about methodology, results, equations, or datasets..."
                                                : "Please wait for paper analysis to complete..."
                                        }
                                        disabled={!isAnalyzed || loadingQa || isAnalyzing}
                                    />
                                    <div className="workspace-query-hint">
                                        ENTER TO SEND <br /> SHIFT + ENTER FOR NEW LINE
                                    </div>
                                    {isAnalyzed && question.trim() && (
                                        <button
                                            onClick={() => handleAskQuestion()}
                                            disabled={loadingQa}
                                            style={{ ...actionBtnStyle(loadingQa), marginTop: "0.6rem" }}
                                        >
                                            {loadingQa ? "SEARCHING..." : "ASK →"}
                                        </button>
                                    )}
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

function GapSection({ title, items, description }) {
    if (!items?.length) return null;
    return (
        <div className="insight-card">
            <h3>{title}</h3>
            {description && (
                <p style={{ fontSize: "0.72rem", opacity: 0.6, marginBottom: "0.6rem" }}>
                    {description}
                </p>
            )}
            <ul style={{ paddingLeft: "1.2rem", lineHeight: 1.7, fontSize: "0.82rem", margin: 0 }}>
                {items.map((item, i) => (
                    <li key={i} style={{ marginBottom: "0.4rem" }}>
                        {typeof item === "object" ? JSON.stringify(item) : item}
                    </li>
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
    color: "#dc2626",
    fontSize: "0.75rem",
    background: "rgba(220, 38, 38, 0.08)",
    padding: "0.5rem",
    border: "1px solid rgba(220, 38, 38, 0.3)",
    marginTop: "0.4rem",
};

export default Workspace;
