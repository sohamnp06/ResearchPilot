import PaperCard from "../PaperCard/PaperCard";
import "./PaperList.css";

function PaperList({ papers = [] }) {
    if (!papers.length) {
        return (
            <section className="paper-list">
                <p>NO PAPERS FOUND.</p>
            </section>
        );
    }

    return (
        <section className="paper-list">
            {papers.map((paper) => (
                <PaperCard key={paper.id} paper={paper} />
            ))}
        </section>
    );
}

export default PaperList;