import "./SearchBar.css";

function SearchBar(){
    return(
        <section className="search-bar">
            <label>QUERY</label>

            <div className="terminal-input">
                <span className="terminal-prompt">&gt;</span>

                <textarea placeholder="How do self healing networks work?" spellCheck="false"/>

            </div>

            <div className="helper">
                <span>Type your question and search the archive</span>
                <span>SHIFT + ENTER FOR NEW LINE</span>
            </div>

        </section>
    );
}
export default SearchBar;