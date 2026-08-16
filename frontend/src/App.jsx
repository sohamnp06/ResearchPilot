import { BrowserRouter, Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";
import Search from "./pages/Search";
import Paper from "./pages/Paper";
import Workspace from "./pages/Workspace";
import Reader from "./pages/Reader";
import ReaderWorkspace from "./pages/ReaderWorkspace";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import VerifyEmail from "./pages/VerifyEmail";
import Library from "./pages/Library";
import Archive from "./pages/Archive";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/search" element={<Search />} />
                <Route path="/paper/:id" element={<Paper />} />
                <Route path="/library" element={<Library />} />
                <Route path="/archive" element={<Archive />} />
                <Route path="/workspace" element={<Workspace />} />
                <Route path="/reader" element={<Reader />} />
                <Route path="/reader/:id" element={<ReaderWorkspace />} />
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/verify-email" element={<VerifyEmail />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;