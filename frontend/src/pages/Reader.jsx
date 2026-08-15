import Navbar from "../components/Navbar/Navbar";
import "../styles/pages/reader.css";
import { useNavigate } from "react-router-dom";


function Reader() {
    
    const navigate = useNavigate();

    const paper = {
        id: "RP - 001",
        title: "When to Admit Art as Evidence",
        year: "2026",
        source: "arxiv",
    };

    return (
        <main className="reader-page">

            <Navbar />

            <div className="reader-toolbar">
                <button className="reader-upload">
                    UPLOAD
                </button>
            </div>

            <section className="reading-history">

                <article className="reading-card">

                    <div className="reading-info">

                        <span className="reading-id">
                            {paper.id}
                        </span>

                        <h1>{paper.title}</h1>

                        <div className="reading-meta">
                            <span>{paper.year}</span>
                            <span>|</span>
                            <span>{paper.source}</span>
                        </div>

                    </div>

                    <button className="continue-button" onClick={() => navigate("/reader/001")}>CONTINUE</button>

                </article>

            </section>

        </main>
    );
}

export default Reader;