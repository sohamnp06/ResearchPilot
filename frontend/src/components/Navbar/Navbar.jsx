import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { getAuthToken, logoutUser } from "../../lib/api";
import "./Navbar.css";

function Navbar() {
    const navigate = useNavigate();
    const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getAuthToken()));

    useEffect(() => {
        const syncAuthState = () => {
            setIsAuthenticated(Boolean(getAuthToken()));
        };

        syncAuthState();
        window.addEventListener("auth-change", syncAuthState);

        return () => {
            window.removeEventListener("auth-change", syncAuthState);
        };
    }, []);

    const handleLogout = () => {
        logoutUser();
        navigate("/login");
    };

    return (
        <header className="nav">
            <Link to="/" className="logo">
                Archivum
            </Link>

            <nav className="nav-links">
                <Link to="/">HOME</Link>
                <Link to="/library">LIBRARY</Link>
                <Link to="/workspace">WORKSPACE</Link>
                <Link to="/reader">READER</Link>

                <div className="auth-actions">
                    {isAuthenticated ? (
                        <button type="button" onClick={handleLogout} className="logout-button">
                            LOGOUT
                        </button>
                    ) : (
                        <Link to="/login" className="auth-button auth-button-dark">
                            LOGIN
                        </Link>
                    )}
                </div>
            </nav>
        </header>
    );
}

export default Navbar;