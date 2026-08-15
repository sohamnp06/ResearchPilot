import "./SearchBar.css";

function SearchBar() {

    return (

        <section className="search-bar">

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

        </section>

    );

}

export default SearchBar;