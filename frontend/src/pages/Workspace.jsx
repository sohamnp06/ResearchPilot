import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";

import "../styles/pages/workspace.css";

function Workspace() {

    const paper = {
        title: "Attention Is All You Need",
        year: "2026",
        source: "arxiv",

        abstract:
            "The dominant sequence transduction models are based on recurrent or convolutional layers. We propose a new simple architecture, the Transformer, based solely on attention mechanisms dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable, requiring substantially less time to train.",

        sections: [
            "01 INTRODUCTION",
            "02 BACKGROUND",
            "03 MODEL ARCHITECTURE",
            "04 EXPERIMENTS",
            "06 RELATED WORK",
            "07 CONCLUSION",
            "08 REFERENCES"
        ]
    };

    return (
        <main className="workspace-page">

            <Navbar />


            {/* TOP BAR */}
            <div className="workspace-toolbar">

                <div className="workspace-paper-name">
                    PAPER : {paper.title.toUpperCase()}
                </div>

            </div>


            {/* MAIN WORKSPACE */}

            <section className="workspace-layout">


                {/* LEFT SIDE */}

                <aside className="workspace-paper">

                    <div className="workspace-label">
                        PAPER
                    </div>

                    <h1 className="workspace-title">
                        {paper.title}
                    </h1>

                    <div className="workspace-meta">
                        <span>{paper.year}</span>
                        <span>|</span>
                        <span>{paper.source}</span>
                    </div>


                    <section className="workspace-section">

                        <h2>ABSTRACT</h2>

                        <p>
                            {paper.abstract}
                        </p>

                    </section>


                    <section className="workspace-section">

                        <h2>SECTIONS</h2>

                        <div className="workspace-sections">

                            {paper.sections.map((section) => (
                                <span key={section}>
                                    {section}
                                </span>
                            ))}

                        </div>

                    </section>

                </aside>


                {/* RIGHT SIDE */}

                <section className="workspace-ai">


                    {/* TABS */}

                    <div className="workspace-tabs">

                        <button className="active">
                            SUMMARY
                        </button>

                        <button>
                            INSIGHTS
                        </button>

                        <button>
                            RELATED
                        </button>

                        <button>
                            CITATIONS
                        </button>

                    </div>


                    {/* SUMMARY */}

                    <div className="workspace-summary">

                        <p>
                            This paper introduces the Transformer model,
                            which relies solely on attention mechanisms. It
                            achieves state of the art results on machine
                            translation tasks while being more efficient
                            and parallelizable.
                        </p>

                    </div>


                    {/* AI INSIGHTS */}

                    <div className="workspace-insights">

                        <div className="insight-card">

                            <h3>
                                RESEARCH GAP
                            </h3>

                            <p>
                                Existing sequence transduction models rely
                                heavily on recurrent or convolutional
                                architectures, limiting parallelization and
                                increasing training time.
                            </p>

                        </div>


                        <div className="insight-card">

                            <h3>
                                KEY INSIGHT
                            </h3>

                            <p>
                                Self-attention allows the model to weigh the
                                importance of different words in the input
                                sequence regardless of their position.
                            </p>

                        </div>

                    </div>


                    {/* QUERY */}

                    <div className="workspace-query">

                        <label>
                            QUERY
                        </label>

                        <textarea
                            placeholder="> ask something about this paper..."
                        />

                        <div className="workspace-query-hint">
                            SHIFT + ENTER
                            <br />
                            FOR NEW LINE
                        </div>

                    </div>

                </section>

            </section>

        </main>
    );
}

export default Workspace;