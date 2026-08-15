import { useEffect, useState } from "react";
import PaperCard from "../PaperCard/PaperCard";
import { searchPapers } from "../../lib/api";
import "./PaperList.css";

function PaperList({ query = "transformer" }) {
    const [papers, setPapers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let isMounted = true;

        async function load() {
            try {
                const results = await searchPapers(query);
                if (isMounted) setPapers(results);
            } catch (error) {
                console.error(error);
                if (isMounted) setPapers([]);
            } finally {
                if (isMounted) setLoading(false);
            }
        }

        load();
        return () => {
            isMounted = false;
        };
    }, [query]);

    if (loading) {
        return <section className="paper-list"><p>Loading papers...</p></section>;
    }

    if (!papers.length) {
        return <section className="paper-list"><p>No papers found.</p></section>;
    }

    return (
        <section className="paper-list">
            {papers.map((paper) => (
                <PaperCard key={paper.id} paper={paper} />
            ))}
        </section>
    );
}

export default PaperList;