import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar/Navbar";
import { getLibrary } from "../lib/api";

import "../styles/pages/archive.css";

function Archive() {
    const [papers, setPapers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [hoveredPaperId, setHoveredPaperId] = useState(null);
    const [openingPaperId, setOpeningPaperId] = useState(null);

    const paperRefs = useRef(new Map());
    const worldRef = useRef(null);
    const stageRef = useRef(null);

    const navigate = useNavigate();

    useEffect(() => {
        async function loadArchive() {
            try {
                const data = await getLibrary();
                setPapers(data);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        }

        loadArchive();
    }, []);

    function getPaperAtPoint(clientX, clientY) {
        let closestPaper = null;
        let closestDistance = Infinity;

        paperRefs.current.forEach((element, paperId) => {
            if (!element) return;

            const rect = element.getBoundingClientRect();

            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            const dx = clientX - centerX;
            const dy = clientY - centerY;

            const normalizedX =
                dx / (rect.width * 0.55);

            const normalizedY =
                dy / (rect.height * 0.55);

            const distance =
                normalizedX * normalizedX +
                normalizedY * normalizedY;

            if (
                distance <= 1 &&
                distance < closestDistance
            ) {
                closestDistance = distance;
                closestPaper = paperId;
            }
        });

        return closestPaper;
    }

    function updateParallax(clientX, clientY) {
        const stage = stageRef.current;
        const world = worldRef.current;

        if (!stage || !world) return;

        const rect = stage.getBoundingClientRect();

        const normalizedX =
            (clientX - rect.left) / rect.width - 0.5;

        const normalizedY =
            (clientY - rect.top) / rect.height - 0.5;

        const translateX = -normalizedX * 18;
        const translateY = -normalizedY * 12;

        const rotateY = normalizedX * 2;
        const rotateX = -normalizedY * 1.5;

        world.style.setProperty(
            "--archive-parallax-x",
            `${translateX.toFixed(2)}px`
        );

        world.style.setProperty(
            "--archive-parallax-y",
            `${translateY.toFixed(2)}px`
        );

        world.style.setProperty(
            "--archive-parallax-rotate-x",
            `${rotateX.toFixed(2)}deg`
        );

        world.style.setProperty(
            "--archive-parallax-rotate-y",
            `${rotateY.toFixed(2)}deg`
        );
    }

    function resetParallax() {
        const world = worldRef.current;

        if (!world) return;

        world.style.setProperty(
            "--archive-parallax-x",
            "0px"
        );

        world.style.setProperty(
            "--archive-parallax-y",
            "0px"
        );

        world.style.setProperty(
            "--archive-parallax-rotate-x",
            "0deg"
        );

        world.style.setProperty(
            "--archive-parallax-rotate-y",
            "0deg"
        );
    }

    function handleArchivePointerMove(event) {
        /*
         * Once the opening animation begins,
         * stop changing the active paper.
         */
        if (openingPaperId) return;

        updateParallax(
            event.clientX,
            event.clientY
        );

        const paperId = getPaperAtPoint(
            event.clientX,
            event.clientY
        );

        setHoveredPaperId(paperId);
    }

    function handleArchivePointerLeave() {
        if (openingPaperId) return;

        setHoveredPaperId(null);
        resetParallax();
    }

    function handleArchiveClick(event) {
        if (openingPaperId) return;

        const paperId = getPaperAtPoint(
            event.clientX,
            event.clientY
        );

        if (!paperId) return;

        /*
         * Freeze the archive around the selected paper.
         */
        setOpeningPaperId(paperId);
        setHoveredPaperId(paperId);

        /*
         * Give the browser time to render the opening
         * state before changing routes.
         */
        window.setTimeout(() => {
            navigate(`/reader/${paperId}`);
        }, 1050);
    }

    if (loading) {
        return (
            <main className="archive-page">
                <Navbar />

                <div className="archive-state">
                    LOADING ARCHIVE...
                </div>
            </main>
        );
    }

    return (
        <main className="archive-page">
            <Navbar />

            <header className="archive-header">
                <div>
                    <p className="archive-kicker">
                        VISUAL COLLECTION
                    </p>

                    <h1>ARCHIVE</h1>
                </div>

                <button
                    type="button"
                    className="archive-back"
                    onClick={() => navigate("/library")}
                    disabled={Boolean(openingPaperId)}
                >
                    BACK TO LIBRARY
                </button>
            </header>

            {papers.length === 0 ? (
                <div className="archive-state">
                    <p>ARCHIVE EMPTY</p>

                    <span>
                        No papers in your library.
                    </span>
                </div>
            ) : (
                <section
                    className={[
                        "archive-stage",
                        openingPaperId
                            ? "is-opening"
                            : "",
                    ]
                        .filter(Boolean)
                        .join(" ")}
                    ref={stageRef}
                >
                    <div
                        className="archive-world"
                        ref={worldRef}
                        onPointerMove={
                            handleArchivePointerMove
                        }
                        onPointerLeave={
                            handleArchivePointerLeave
                        }
                        onClick={handleArchiveClick}
                    >
                        {papers.map((paper, index) => {
                            const isHovered =
                                hoveredPaperId === paper.id;

                            const isDimmed =
                                hoveredPaperId !== null &&
                                !isHovered;

                            const isOpening =
                                openingPaperId === paper.id;

                            return (
                                <article
                                    key={paper.id}
                                    ref={(element) => {
                                        if (element) {
                                            paperRefs.current.set(
                                                paper.id,
                                                element
                                            );
                                        } else {
                                            paperRefs.current.delete(
                                                paper.id
                                            );
                                        }
                                    }}
                                    className={[
                                        "archive-paper",
                                        `archive-paper-${index % 6}`,

                                        isHovered
                                            ? "is-hovered"
                                            : "",

                                        isDimmed
                                            ? "is-dimmed"
                                            : "",

                                        isOpening
                                            ? "is-opening"
                                            : "",
                                    ]
                                        .filter(Boolean)
                                        .join(" ")}
                                >
                                    <div className="archive-paper-inner">
                                        <div className="archive-paper-top">
                                            <span>
                                                {paper.id}
                                            </span>

                                            <span>
                                                {paper.year || "N/A"}
                                            </span>
                                        </div>

                                        <div className="archive-paper-content">
                                            <h2>
                                                {paper.title}
                                            </h2>

                                            <p>
                                                {Array.isArray(
                                                    paper.authors
                                                ) &&
                                                paper.authors.length
                                                    ? paper.authors[0]
                                                    : "AUTHOR UNKNOWN"}
                                            </p>
                                        </div>

                                        <div className="archive-paper-footer">
                                            <span>
                                                {paper.source ||
                                                    "ARCHIVE"}
                                            </span>

                                            <span>
                                                OPEN →
                                            </span>
                                        </div>
                                        <div className="archive-paper-reveal">
                                            <div className="archive-reveal-header">
                                                 <span>DOCUMENT</span>
                                                 <span>READ / 01</span>
                                            </div>

                                            <div className="archive-reveal-body">
                                                <div className="archive-reveal-title">
                                                    {paper.title}
                                                </div>
                                                
                                                <div className="archive-reveal-lines">
                                                    <span></span>
                                                    <span></span>
                                                    <span></span>
                                                    <span></span>
                                                    <span></span>
                                                    <span></span>
                                                </div>
                                            </div>

                                            <div className="archive-reveal-footer">
                                                <span>OPENING READER</span>
                                                <span></span>
                                            </div>
                                        </div>
                                    </div>
                                </article>
                            );
                        })}
                    </div>

                    <div className="archive-instruction">
                        <span>
                            SELECT A PAPER TO OPEN
                        </span>

                        <span>
                            SCROLL TO EXPLORE
                        </span>
                    </div>
                </section>
            )}
        </main>
    );
}

export default Archive;