import { Link } from "react-router-dom";

import "./Navbar.css";

function Navbar() {
    return (
        <header className="nav">

            <Link to="/" className="logo">
                Archivum
            </Link>

            <nav className="nav-links">

                <Link to="/">
                    HOME
                </Link>

                <Link to="/library">
                    LIBRARY
                </Link>

                <Link to="/workspace">
                    WORKSPACE
                </Link>

                <Link to="/reader">
                    READER
                </Link>

            </nav>

        </header>
    );
}

export default Navbar;