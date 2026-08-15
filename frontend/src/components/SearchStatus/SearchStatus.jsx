import "./SearchStatus.css";

function SearchStatus({ count = 0 }) {
    return (
        <section className="search-status">
            <h2>SEARCHING ARCHIVE...</h2>
            <p>{count} PAPER{count === 1 ? "" : "S"} FOUND</p>
        </section>
    );
}

export default SearchStatus;