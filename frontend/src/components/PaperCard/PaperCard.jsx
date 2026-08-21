import "./PaperCard.css";
import { useNavigate } from "react-router-dom";

function PaperCard({ paper, onOpen, importing, isSimilar, displayId }) {

    const navigate = useNavigate();

    const paperId = paper.id || paper.paper_id;

    const authors = Array.isArray(paper.authors)
        ? paper.authors.slice(0, 3).join(", ")
        : "";

    function handleOpen() {
        if (onOpen) {
            onOpen(paper);
        } else {
            navigate(`/paper/${paperId}`);
        }
    }

    return (
        <article
            className={`paper-card ${isSimilar ? "is-similar" : ""}`}
        >

            {/* SOURCE */}
            <p className="paper-card-id">
                {displayId}
            </p>

            {/* MAIN CONTENT */}
            <div>
                <h3 className="paper-card-title">
                    {paper.title}
                </h3>

                <div className="paper-card-meta">

                    <span>
                        {paper.year || "—"}
                    </span>

                    {authors && (
                        <>
                            <span className="meta-separator">·</span>
                            <span>{authors}</span>
                        </>
                    )}

                    {paper.citation_count != null && (
                        <>
                            <span className="meta-separator">·</span>
                            <span>
                                {paper.citation_count} CITATIONS
                            </span>
                        </>
                    )}

                </div>
            </div>

            {/* ACTIONS */}
            {onOpen && (
                <div className="paper-card-actions">

                    {paper.has_pdf && (
                        <span className="paper-card-pdf">
                            PDF
                        </span>
                    )}

                    <button
                        className="paper-card-action"
                        onClick={handleOpen}
                        disabled={importing}
                    >
                        {importing
                            ? "OPENING..."
                            : "OPEN PAPER →"}
                    </button>

                </div>
            )}

        </article>
    );
}

export default PaperCard;