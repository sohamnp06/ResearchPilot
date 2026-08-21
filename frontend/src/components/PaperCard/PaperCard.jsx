import "./PaperCard.css";
import { useNavigate } from "react-router-dom";

function PaperCard({ paper, onOpen, importing, isSimilar }) {
    const navigate = useNavigate();

    const paperId = paper.id || paper.paper_id;

    let authors = "";
    if (Array.isArray(paper.authors)) {
        authors = paper.authors.slice(0, 3).join(", ");
    } else if (typeof paper.authors === "string") {
        authors = paper.authors;
    }

    function handleOpen() {
        if (onOpen) {
            onOpen(paper);
        } else {
            navigate(`/paper/${paperId}`);
        }
    }

    return (
        <article className={`paper-card ${isSimilar ? "is-similar" : ""}`}>
            <div className="paper-card-info">
                <h1 className="paper-card-title">
                    {paper.title}
                </h1>

                <div className="paper-card-meta">
                    <span>{paper.year || "—"}</span>

                    <span>|</span>

                    <span>{paper.source || "archive"}</span>

                    {authors && (
                        <>
                            <span>|</span>
                            <span>{authors}</span>
                        </>
                    )}
                </div>
            </div>

            <div className="paper-card-actions">
                {(paper.has_pdf || paper.pdf_url) && (
                    <span className="paper-card-pdf">
                        PDF
                    </span>
                )}

                <button
                    className="paper-card-action"
                    onClick={handleOpen}
                    disabled={importing}
                >
                    {importing ? "OPENING..." : "OPEN PAPER →"}
                </button>
            </div>
        </article>
    );
}

export default PaperCard;