import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";
import { useNavigate } from "react-router-dom";

import "../styles/pages/paper.css";

function Paper() {

    const navigate = useNavigate();

    const paper = {
        id: "001",
        title: "Attention Is All You Need",
        year: "2026",
        source: "arxiv",

        authors: [
            "Ashish Vaswani",
            "Illia Polosukhin",
            "Noam Shazeer",
            "Niki Parmar",
            "Jakob Uszkoreit"
        ],

        abstract:
            "The dominant sequence transduction models are based on recurrent or convolutional layers. We propose a new simple architecture, the Transformer, based solely on attention mechanisms dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable, requiring substantially less time to train.",

        citedBy: "676968",
        references: "30",
        pages: "15"
    };

    return (
        <main className="paper-page">

            <Navbar />

            <div className="paper-toolbar">

                <BackButton />

                <div className="paper-actions">

                    <span>
                        PAPER ID : {paper.id}
                    </span>

                    <div className="paper-action-buttons">

                        <button>
                            ADD TO LIBRARY
                        </button>

                        <button onClick={() => navigate(`/reader/${paper.id}`)}>READ PAPER</button>

                        <button onClick={() => navigate("/workspace")}>OPEN WORKSPACE</button>

                    </div>

                </div>

            </div>


            <section className="paper-layout">

                {/* LEFT SIDE */}

                <div className="paper-info">

                    <div className="paper-number">
                        {paper.id}
                    </div>

                    <h1 className="paper-title">
                        {paper.title}
                    </h1>

                    <div className="paper-meta">
                        <span>{paper.year}</span>
                        <span>|</span>
                        <span>{paper.source}</span>
                    </div>


                    <section className="paper-section">

                        <h2>AUTHORS</h2>

                        <p className="paper-authors">
                            {paper.authors.map((author, index) => (
                                <span key={author}>
                                    {author}

                                    {index < paper.authors.length - 1 && " , "}

                                    {index !== paper.authors.length - 1 &&
                                        index % 2 === 1 && <br />}
                                </span>
                            ))}
                        </p>

                    </section>


                    <section className="paper-section">

                        <h2>ABSTRACT</h2>

                        <p className="paper-abstract">
                            {paper.abstract}
                        </p>

                    </section>


                    <div className="paper-stats">

                        <div>
                            <span className="stat-label">
                                CITED BY
                            </span>

                            <strong>
                                {paper.citedBy}
                            </strong>
                        </div>


                        <div>
                            <span className="stat-label">
                                REFERENCES
                            </span>

                            <strong>
                                {paper.references}
                            </strong>
                        </div>


                        <div>
                            <span className="stat-label">
                                PAGES
                            </span>

                            <strong>
                                {paper.pages}
                            </strong>
                        </div>


                        <div>
                            <span className="stat-label">
                                PDF
                            </span>

                            <strong>
                                DOWNLOAD
                            </strong>
                        </div>

                    </div>

                </div>


                {/* RIGHT SIDE */}

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