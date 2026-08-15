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
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#0f172a", color: "#fff" }}>
      <div style={{ width: "100%", maxWidth: "430px", background: "#111827", padding: "2rem", borderRadius: "16px", boxShadow: "0 12px 32px rgba(0,0,0,0.25)" }}>
        <h1 style={{ marginBottom: "1.5rem", textAlign: "center" }}>Create account</h1>

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem" }}>
          <input
            type="text"
            name="username"
            value={form.username}
            onChange={handleChange}
            placeholder="Username"
            required
            style={{ padding: "0.9rem 1rem", borderRadius: "10px", border: "1px solid #374151", background: "#1f2937", color: "#fff" }}
          />

          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            placeholder="Email"
            required
            style={{ padding: "0.9rem 1rem", borderRadius: "10px", border: "1px solid #374151", background: "#1f2937", color: "#fff" }}
          />

          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            placeholder="Password"
            required
            style={{ padding: "0.9rem 1rem", borderRadius: "10px", border: "1px solid #374151", background: "#1f2937", color: "#fff" }}
          />

          {error && (
            <div style={{ color: "#fca5a5", fontSize: "0.9rem" }}>{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{ padding: "0.9rem 1rem", borderRadius: "10px", border: "none", background: "#34d399", color: "#062b1d", fontWeight: 700, cursor: "pointer" }}
          >
            {loading ? "Creating account..." : "Sign up"}
          </button>
        </form>

        <p style={{ marginTop: "1rem", textAlign: "center" }}>
          Already have an account? <Link to="/login" style={{ color: "#93c5fd" }}>Login</Link>
        </p>
      </div>
    </main>
  );
}

export default Signup;
