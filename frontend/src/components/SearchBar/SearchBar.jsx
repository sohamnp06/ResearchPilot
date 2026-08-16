import { useState } from "react";
import { useNavigate } from "react-router-dom";

import "./SearchBar.css";

function SearchBar(){
    const [query, setQuery] = useState("");
    const navigate = useNavigate();

    function submitSearch() {
        const trimmedQuery = query.trim();
        if (!trimmedQuery) return;
        navigate(`/search?q=${encodeURIComponent(trimmedQuery)}`);
    }

    function handleKeyDown(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submitSearch();
        }
    }

    return(
        <section className="search-bar">
            <label>QUERY</label>

            <div className="terminal-input">
                <span className="terminal-prompt">&gt;</span>

                <textarea
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="How do self healing networks work?"
                    spellCheck="false"
                    aria-label="Search research papers"
                />

            </div>

            <div className="helper">
                <span>Press Enter to search the archive</span>
                <span>SHIFT + ENTER FOR NEW LINE</span>
            </div>

        </section>
    );
}
export default SearchBar;
