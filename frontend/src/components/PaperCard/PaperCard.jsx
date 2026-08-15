import "./PaperCard.css";

import { useNavigate } from "react-router-dom";

function PaperCard({ paper }) {

    const navigate = useNavigate();

    function openPaper() {
        navigate(`/paper/${paper.id}`);
    }

    return (
        <article
            className="paper-card"
            onClick={openPaper}
        >

            <p>{paper.id}</p>

            <h3>{paper.title}</h3>

            <span>{paper.year}</span>

            <span>{paper.source}</span>

            <span className="paper-arrow">
                →
            </span>

        </article>
    );
}

export default PaperCard;