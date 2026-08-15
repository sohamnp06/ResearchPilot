import { useEffect, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";

import "./PDFViewer.css";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    "pdfjs-dist/build/pdf.worker.min.mjs",
    import.meta.url
).toString();

function PDFViewer({ file }) {

    const documentRef = useRef(null);

    const [numPages, setNumPages] = useState(null);
    const [pageWidth, setPageWidth] = useState(400);

    function onDocumentLoadSuccess({ numPages }) {
        setNumPages(numPages);
    }

    useEffect(() => {

        function updateWidth() {

            if (!documentRef.current) return;

            const width = documentRef.current.clientWidth;

            setPageWidth(Math.max(width - 32, 300));
        }

        updateWidth();

        const observer = new ResizeObserver(updateWidth);

        if (documentRef.current) {
            observer.observe(documentRef.current);
        }

        return () => observer.disconnect();

    }, []);

    return (

        <div className="pdf-viewer">

            <div className="pdf-toolbar">

                <div className="pdf-page-count">
                    {numPages ? `${numPages} PAGES` : "LOADING"}
                </div>

                <div className="pdf-scroll-hint">
                    ↕
                </div>

            </div>


            <div
                className="pdf-document"
                ref={documentRef}
            >

                <Document
                    file={file}
                    onLoadSuccess={onDocumentLoadSuccess}
                    loading="LOADING PAPER..."
                    error="COULD NOT LOAD PAPER."
                >

                    {numPages &&
                        Array.from(
                            new Array(numPages),
                            (_, index) => (
                                <Page
                                    key={`page_${index + 1}`}
                                    pageNumber={index + 1}
                                    width={pageWidth}
                                    renderTextLayer={false}
                                    renderAnnotationLayer={false}
                                />
                            )
                        )
                    }

                </Document>

            </div>

        </div>
    );
}

export default PDFViewer;