import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";
import SortBar from "../components/SortBar/SortBar";
import SearchStatus from "../components/SearchStatus/SearchStatus";
import PaperList from "../components/PaperList/PaperList";

import "../styles/pages/search.css";

function Search(){

    return(
    
        <main className="search-page">

            <Navbar />

            <div className="search-header">

                <BackButton />

                <SortBar />

            </div>

            <SearchStatus />

            <PaperList />

        </main>

    )

}

export default Search;