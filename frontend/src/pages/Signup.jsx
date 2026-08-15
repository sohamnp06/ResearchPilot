import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signupUser } from "../lib/api";

function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await signupUser(form);
      navigate("/verify-email", { state: { email: form.email } });
    } catch (err) {
      setError(err.message || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#FFF6EA", color: "#000" }}>
      <div style={{ width: "100%", maxWidth: "520px", background: "#FFF6EA", border: "2px solid #000", padding: "2rem 2rem 1.4rem", boxShadow: "8px 8px 0 #000" }}>
        <h1 style={{ margin: "0 0 1.5rem", textAlign: "center", fontFamily: '"Instrument Serif", serif', fontSize: "64px", fontWeight: 400, lineHeight: 1, letterSpacing: "-0.04em" }}>
          SIGN UP
        </h1>

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem" }}>
          <div style={{ display: "grid", gap: "0.5rem" }}>
            <label style={{ fontFamily: '"Lexend Exa", sans-serif', fontSize: "12px", letterSpacing: ".12em", textTransform: "uppercase" }}>USERNAME</label>
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="Choose a username"
              required
              style={{ padding: "0.9rem 1rem", border: "2px solid #000", background: "#FFF6EA", color: "#000", fontFamily: '"JetBrains Mono", monospace', fontSize: "16px", outline: "none" }}
            />
          </div>

          <div style={{ display: "grid", gap: "0.5rem" }}>
            <label style={{ fontFamily: '"Lexend Exa", sans-serif', fontSize: "12px", letterSpacing: ".12em", textTransform: "uppercase" }}>EMAIL</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
              style={{ padding: "0.9rem 1rem", border: "2px solid #000", background: "#FFF6EA", color: "#000", fontFamily: '"JetBrains Mono", monospace', fontSize: "16px", outline: "none" }}
            />
          </div>

          <div style={{ display: "grid", gap: "0.5rem" }}>
            <label style={{ fontFamily: '"Lexend Exa", sans-serif', fontSize: "12px", letterSpacing: ".12em", textTransform: "uppercase" }}>PASSWORD</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Create a password"
              required
              style={{ padding: "0.9rem 1rem", border: "2px solid #000", background: "#FFF6EA", color: "#000", fontFamily: '"JetBrains Mono", monospace', fontSize: "16px", outline: "none" }}
            />
          </div>

          {error && (
            <div style={{ color: "#B91C1C", fontSize: "0.9rem", fontFamily: '"Lexend Exa", sans-serif' }}>{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{ padding: "0.9rem 1rem", border: "2px solid #000", background: "#111827", color: "#fff", fontFamily: '"Lexend Exa", sans-serif', fontSize: "18px", letterSpacing: ".08em", cursor: "pointer", boxShadow: "4px 4px 0 #000" }}
          >
            {loading ? "CREATING ACCOUNT..." : "SIGN UP"}
          </button>
        </form>

        <p style={{ marginTop: "1.25rem", textAlign: "center", fontFamily: '"Lexend Exa", sans-serif', fontSize: "14px", letterSpacing: ".04em" }}>
          Already have an account? <Link to="/login" style={{ color: "#000", textDecoration: "underline" }}>Login</Link>
        </p>
      </div>
    </main>
  );
}

export default Signup;
