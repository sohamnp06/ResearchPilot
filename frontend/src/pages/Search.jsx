import { useState } from "react";
import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";
import SortBar from "../components/SortBar/SortBar";
import SearchStatus from "../components/SearchStatus/SearchStatus";
import PaperList from "../components/PaperList/PaperList";

import "../styles/pages/search.css";

function Search() {
    const [query, setQuery] = useState("transformer");

    return (
        <main className="search-page">
            <Navbar />

            <div className="search-header">
                <BackButton />
                <SortBar />
            </div>

            <SearchStatus count={0} />

            <div style={{ padding: "0 1rem 1rem" }}>
                <input
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="Search papers"
                    style={{
                        width: "100%",
                        padding: "0.9rem 1rem",
                        borderRadius: "10px",
                        border: "1px solid #d0d7de",
                        fontSize: "1rem",
                    }}
                />
            </div>

            <PaperList query={query} />
        </main>
    );
}

export default Search;