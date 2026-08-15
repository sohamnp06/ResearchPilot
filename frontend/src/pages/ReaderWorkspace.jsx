import Navbar from "../components/Navbar/Navbar";

import "../styles/pages/reader-workspace.css";

import PDFviewer from "../components/PDFviewer/PDFviewer"

import BackButton from "../components/BackButton/BackButton";

function ReaderWorkspace() {
    return (
        <main className="reader-workspace">

            <Navbar />

            <div className="reader-toolbar">
                <BackButton />
            </div>

            <div className="reader-container">

                <section className="pdf-panel">

                    <PDFviewer file="/pdfs/attention-is-all-you-need.pdf"/>

                </section>

                <section className="notes-panel">

                    <h2>NOTES</h2>

                    <textarea
                        className="notes-editor"
                        placeholder=""
                    />

                </section>

            </div>

        </main>
    );
}

export default ReaderWorkspace;