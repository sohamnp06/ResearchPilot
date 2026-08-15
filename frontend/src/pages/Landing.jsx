import "../styles/pages/landing.css";
import Navbar from "../components/Navbar/Navbar";

function Landing() {
    return (
        <div className="landing">

            <Navbar/>

            <section className="hero">

                <div className="hero-left">

                    <h1>Archivum</h1>

                    <div className="tagline">

                        <span>//</span>

                        <p>ENTER THE ARCHIVE</p>

                    </div>

                </div>

                <div className="hero-right">

                    <div className="description">

                        AI-POWERED<br/>
                        RESEARCH<br/>
                        PAPER ASSISTANT<br/>
                        BUILT FOR<br/>
                        DEEP RESEARCH<br/>
                        AND REAL<br/>
                        DISCOVERY

                    </div>

                </div>

            </section>

            <div className="search">

                <label>QUERY</label>

                <textarea
                    placeholder="> How do self healing networks work?"
                />

                <div className="helper">

                    <span>
                        Type your question and search the archive
                    </span>

                    <span>
                        SHIFT + ENTER FOR NEW LINE
                    </span>

                </div>

            </div>

        </div>
    );
}

export default Landing;