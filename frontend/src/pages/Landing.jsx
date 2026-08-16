import { Link } from "react-router-dom";

import "../styles/pages/landing.css";
import Navbar from "../components/Navbar/Navbar";
import SearchBar from "../components/SearchBar/SearchBar";

function Landing() {
    return (
        <div className="landing">
            <Navbar />

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
                        AI-POWERED<br />
                        RESEARCH<br />
                        PAPER ASSISTANT<br />
                        BUILT FOR<br />
                        DEEP RESEARCH<br />
                        AND REAL<br />
                        DISCOVERY
                    </div>
                </div>
            </section>

            <SearchBar />

        </div>
    );
}

export default Landing;