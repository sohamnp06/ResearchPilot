import { BrowserRouter, Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";
import Search from "./pages/Search";
import Paper from "./pages/Paper";
import Workspace from "./pages/Workspace";
import Reader from "./pages/Reader";
import ReaderWorkspace from "./pages/ReaderWorkspace";

function Library(){
    return(
        <main>
            <h1>LIBRARY</h1>
        </main>
    );
}

function App() {
    return (
        <BrowserRouter>

            <Routes>

                <Route path="/" element={<Landing />} />

                <Route path="/search" element={<Search />} />

                <Route path="/paper/:id" element={<Paper />} />

                <Route path="/library" element={<Library />} />

                <Route path="/workspace" element={<Workspace />} />

                <Route path="/reader" element={<Reader />} />

                <Route path="/reader/:id" element={<ReaderWorkspace/>} />

            </Routes>

        </BrowserRouter>
    );
}

export default App;