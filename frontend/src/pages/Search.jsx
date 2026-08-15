import { useEffect, useState } from "react";
import Navbar from "../components/Navbar/Navbar";
import BackButton from "../components/BackButton/BackButton";
import SortBar from "../components/SortBar/SortBar";
import PaperList from "../components/PaperList/PaperList";
import { searchPapers } from "../lib/api";

import "../styles/pages/search.css";

function Search() {
    const [query] = useState("transformer");
    const [papers,setPapers] = useState([]);
    const [loading,setLoading] = useState(true);

    useEffect(() => {
        let isMounted = true;

            async function load(){
                setLoading(true);

                try {
                    const results = await searchPapers(query);

                    if(isMounted){
                        setPapers(results);
                    }
                } catch (error) {
                    console.error(error);

                    if(isMounted){
                        setPapers([]);
                    }
                }finally{
                    if(isMounted){
                        setLoading(false);
                    }
                }
            }

            load();

            return () => {isMounted = false};

        }
    ,[query]);

    return (
        <main className="search-page">
            <Navbar />

            <div className="search-header">
                <BackButton />
                <SortBar />
            </div>

            <section className={`search-status ${loading ? "is-loading" : "is-loaded"}`}>
                {loading ? (
                    <>
                        <h1>SEARCHING ARCHIVE<span className="search-dots">...</span></h1>
                        <p>SEARCHING</p>
                    </>
                ) : (
                    <>
                        <h1>ARCHIVE RESULTS</h1>
                        <p>{papers.length} PAPERS FOUND</p>
                    </>
                )}
            </section>

            {!loading && <PaperList papers={papers} />}
            
        </main>
    );
}

export default Search;