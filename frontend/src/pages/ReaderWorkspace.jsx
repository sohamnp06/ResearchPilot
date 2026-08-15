import { useEffect, useState } from "react";
import Navbar from "../components/Navbar/Navbar";
import "../styles/pages/reader-workspace.css";
import PDFviewer from "../components/PDFviewer/PDFviewer";
import BackButton from "../components/BackButton/BackButton";
import { getPaperDetails, getPaperNotes, saveReaderProgress, createPaperNote, updatePaperNote } from "../lib/api";
import { useParams } from "react-router-dom";

function ReaderWorkspace() {
    const { id } = useParams();
    const [paper, setPaper] = useState(null);
    const [notes, setNotes] = useState("");
    const [noteId, setNoteId] = useState(null);

    useEffect(() => {
        async function load() {
            try {
                const paperData = await getPaperDetails(id);
                setPaper(paperData);
                await saveReaderProgress(id, 1);

                const noteList = await getPaperNotes(id);
                if (noteList.length) {
                    const first = noteList[0];
                    setNotes(first.content);
                    setNoteId(first.id);
                }
            } catch (error) {
                console.error(error);
            }
        }

        if (id) load();
    }, [id]);

    async function handleNotesChange(event) {
        const content = event.target.value;
        setNotes(content);

        if (!id) return;

        try {
            if (noteId) {
                await updatePaperNote(id, noteId, "Reader note", content);
            } else {
                const created = await createPaperNote(id, "Reader note", content);
                setNoteId(created.id);
            }
        } catch (error) {
            console.error(error);
        }
    }

    const pdfUrl = (() => {
        if (!paper?.pdfUrl) return "/pdfs/attention-is-all-you-need.pdf";

        const value = String(paper.pdfUrl).trim();
        if (!value) return "/pdfs/attention-is-all-you-need.pdf";

        if (value.startsWith("http://") || value.startsWith("https://")) {
            return value.includes("arxiv.org") ? "/pdfs/attention-is-all-you-need.pdf" : value;
        }

        return value;
    })();

    return (
        <main className="reader-workspace">
            <Navbar />

            <div className="reader-toolbar">
                <BackButton />
            </div>

            <div className="reader-container">
                <section className="pdf-panel">
                    <PDFviewer file={pdfUrl} />
                </section>

                <section className="notes-panel">
                    <h2>NOTES</h2>
                    <textarea
                        className="notes-editor"
                        value={notes}
                        onChange={handleNotesChange}
                        placeholder="Write your notes here..."
                    />
                </section>
            </div>
        </main>
    );
}

export default ReaderWorkspace;