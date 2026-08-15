import PaperCard from "../PaperCard/PaperCard";
import "./PaperList.css";

function PaperList() {

    const papers = [
        {
            id: "001",
            title: "Attention Is All You Need",
            year: "2017",
            source: "arXiv",
        },
        {
            id: "002",
            title: "Pre-Training of Deep Bidirectional Transformers",
            year: "2018",
            source: "Google",
        },
        {
            id: "003",
            title: "Graph Neural Networks",
            year: "2020",
            source: "IEEE",
        },
    ];

    return (

        <section className="paper-list">

            {papers.map((paper) => (
                <PaperCard
                    key={paper.id}
                    paper={paper}
                />
            ))}

        </section>

    );

}

export default PaperList;